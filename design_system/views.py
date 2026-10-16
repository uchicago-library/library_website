"""Design system documentation, served at /design/.

Every page is a Markdown file under content/. Its front matter gives the
title, description and, optionally, an order and a template. A folder lists
its own pages, so adding a page means adding a file and nothing else.

A page body is rendered as a Django template first and as Markdown second, so
it can {% include %} a live demo. Wrap template syntax meant to be displayed
in {% verbatim %}.
"""

import json
import math
import re
import xml.etree.ElementTree as etree
from functools import lru_cache, wraps
from pathlib import Path

import markdown
import yaml
from django.conf import settings
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.template import engines
from django.urls import resolve, reverse
from django.utils.safestring import mark_safe
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from wagtailcache.cache import nocache_page

APP_DIR = Path(__file__).resolve().parent
CONTENT_DIR = APP_DIR / "content"
DATA_DIR = APP_DIR / "data"
TOKENS_FILE = DATA_DIR / "tokens.json"
TOKEN_TABLES_SLUG = "implementation/token-tables"
MARKDOWN_EXTENSIONS = ["attr_list", "fenced_code", "tables", "toc"]


class _BootstrapTableProcessor(Treeprocessor):
    """Styles Markdown tables as Bootstrap tables, in a scrolling wrapper.

    Raw HTML tables never reach the tree, so they are left as written.
    """

    def run(self, root):
        for parent in list(root.iter()):
            for index, child in enumerate(list(parent)):
                if child.tag != "table":
                    continue
                child.set("class", "table table-bordered table-sm")
                wrapper = etree.Element("div", {"class": "table-responsive"})
                parent.remove(child)
                wrapper.append(child)
                parent.insert(index, wrapper)


class BootstrapTables(Extension):
    def extendMarkdown(self, md):
        md.treeprocessors.register(_BootstrapTableProcessor(md), "bootstrap_tables", 0)


def _parse(path):
    """Front matter and body of a content file."""
    source = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    meta, body = {}, source
    if source.startswith("---\n"):
        _, front, body = source.split("---\n", 2)
        meta = yaml.safe_load(front) or {}
    return meta, body, source


_parse_cached = lru_cache(maxsize=None)(_parse)


def parse(path):
    # Files only change on deploy, so they are read once per process; in
    # development they are re-read so edits show without a restart.
    return _parse(path) if settings.DEBUG else _parse_cached(path)


def page_url(slug=""):
    if not slug:
        return reverse("design_system:page")
    return reverse("design_system:page", kwargs={"slug": slug})


def locate(slug):
    """The content file for a slug, and whether the slug is a folder.

    A folder without an index.md is still a page: its listing. An index.md is
    its folder's page, so it has no URL of its own.
    """
    if slug.rsplit("/", 1)[-1] == "index":
        raise Http404
    folder = CONTENT_DIR / slug
    if folder.is_dir():
        index = folder / "index.md"
        return (index if index.exists() else None), True
    path = CONTENT_DIR / f"{slug}.md"
    if slug and path.exists():
        return path, False
    raise Http404


def entry(slug):
    """A page's title, description and listing position."""
    path, is_folder = locate(slug)
    meta = parse(path)[0] if path else {}
    name = slug.rsplit("/", 1)[-1]
    return {
        "slug": slug,
        "url": page_url(slug),
        "title": meta.get("title") or name.replace("-", " ").capitalize(),
        "description": meta.get("description", ""),
        "order": meta.get("order", math.inf),
        "template": meta.get("template"),
        "is_folder": is_folder,
    }


def children(slug):
    """The pages directly inside a folder, each subfolder nesting its own."""
    items = []
    for child in (CONTENT_DIR / slug).iterdir():
        child_slug = f"{slug}/{child.stem}" if slug else child.stem
        if child.is_dir():
            item = entry(child_slug)
            item["children"] = children(child_slug)
        elif child.suffix == ".md" and child.name != "index.md":
            item = entry(child_slug)
        else:
            continue
        items.append(item)
    return sorted(items, key=lambda item: (item["order"], item["title"]))


def breadcrumbs(slug):
    parts = slug.split("/") if slug else []
    return [entry("/".join(parts[: i + 1])) for i in range(len(parts))]


def inline_markdown(text):
    """Markdown for a single line of prose, without the wrapping <p>."""
    html = markdown.markdown(text or "")
    if html.startswith("<p>") and html.endswith("</p>"):
        html = html[3:-4]
    return mark_safe(html)


def _load_tokens():
    tokens = json.loads(TOKENS_FILE.read_text(encoding="utf-8"))
    for table in tokens["tables"]:
        for section in table["sections"]:
            section["guidance_html"] = inline_markdown(section.get("guidance"))
            for row in section.get("tokens", []) + section.get("classes", []):
                row["note_html"] = inline_markdown(row["note"])
    return tokens


_load_tokens_cached = lru_cache(maxsize=1)(_load_tokens)


def load_tokens():
    return _load_tokens() if settings.DEBUG else _load_tokens_cached()


def render_template(body, context, request):
    """A page body with its template syntax run, still in Markdown."""
    template = engines["django"].from_string("{% load static %}" + body)
    return template.render(context, request)


def render_body(body, context, request):
    if not body.strip():
        return ""
    html = markdown.markdown(
        render_template(body, context, request),
        extensions=MARKDOWN_EXTENSIONS + [BootstrapTables()],
    )
    return mark_safe(html)


@nocache_page
def not_found(request, *args, **kwargs):
    """The design system's own 404, for any missing page under /design/.

    The last URL pattern sends every unmatched path here, which would stop
    Django adding a missing trailing slash, so that is done here instead.
    """
    if not request.path_info.endswith("/"):
        if resolve(f"{request.path_info}/").func is not not_found:
            return redirect(request.get_full_path(force_append_slash=True))
    return render(request, "design_system/404.html", status=404)


def design_view(view):
    """Wraps every /design/ view.

    Keeps the response out of search engines, whatever its content type. Meta
    tags only reach HTML, so llms.txt, tokens.json and the Markdown sources
    carry the header instead. robots.txt is deliberately not used: agents
    fetching on someone's behalf honour it too, and would be locked out.

    Answers a missing page with the design system's 404, not the site's.

    Skips wagtail-cache, which would otherwise hold a page for six hours after
    a deploy changed it. Rendering is cheap: content files are parsed once per
    process.
    """

    @wraps(view)
    @nocache_page
    def wrapper(request, *args, **kwargs):
        try:
            response = view(request, *args, **kwargs)
        except Http404:
            return not_found(request)
        response["X-Robots-Tag"] = "noindex, nofollow, noarchive"
        return response

    return wrapper


def markdown_url(item):
    """The .md URL of a page's source, following the llms.txt convention."""
    parts = [item["slug"], "index" if item["is_folder"] else ""]
    slug = "/".join(part for part in parts if part)
    return reverse("design_system:markdown", kwargs={"slug": slug})


@design_view
def markdown_source(request, slug):
    path = CONTENT_DIR / f"{slug}.md"
    if not path.is_file():
        raise Http404
    # Includes are run, so a reader gets the table or demo they bring in rather
    # than the tag. The Markdown itself is left as written.
    meta, body, source = parse(path)
    front_matter = source[: len(source) - len(body)]
    text = front_matter + render_template(body, {"meta": meta}, request)
    return HttpResponse(text, content_type="text/markdown; charset=utf-8")


@design_view
def page(request, slug=""):
    slug = slug or ""
    path, is_folder = locate(slug)
    meta, body, source = parse(path) if path else ({}, "", "")

    sections = [item for item in children("") if item["is_folder"]]
    context = {
        "page": entry(slug),
        "meta": meta,
        "children": children(slug) if is_folder else [],
        "breadcrumbs": breadcrumbs(slug),
        "sections": sections,
        "section": slug.split("/")[0],
        "token_tables_url": page_url(TOKEN_TABLES_SLUG),
        "is_token_tables": slug == TOKEN_TABLES_SLUG,
    }
    if context["is_token_tables"]:
        context["tokens"] = load_tokens()
    context["content"] = render_body(body, context, request)
    template = meta.get("template", "design_system/page.html")
    return render(request, template, context)


@design_view
def tokens_json(request):
    tokens = json.loads(TOKENS_FILE.read_text(encoding="utf-8"))
    return JsonResponse({"tokens": tokens["all"], "classes": tokens["classes"]})


def _walk(items):
    for item in items:
        yield item
        yield from _walk(item.get("children", []))


@design_view
def llms_txt(request):
    """Discovery index for agents (https://llmstxt.org), built from content/."""
    absolute = request.build_absolute_uri

    def link(item):
        # Prose pages point at their Markdown source; generated pages and
        # live demos only exist rendered.
        if item["template"] or item["is_folder"]:
            return absolute(item["url"])
        return absolute(markdown_url(item))

    home = parse(CONTENT_DIR / "index.md")[0]
    # The introduction is written in content/index.md, with site-relative links.
    intro = re.sub(
        r"\]\((/[^)]*)\)", lambda m: f"]({absolute(m[1])})", home["llms"].strip()
    )
    lines = [f"# {home['title']}", "", f"> {home['description']}", "", intro]
    for section in children(""):
        if not section["is_folder"]:
            continue
        lines += ["", f"## [{section['title']}]({absolute(section['url'])})", ""]
        for item in _walk(section["children"]):
            description = f": {item['description']}" if item["description"] else ""
            lines.append(f"- [{item['title']}]({link(item)}){description}")
    return HttpResponse(
        "\n".join(lines) + "\n", content_type="text/plain; charset=utf-8"
    )
