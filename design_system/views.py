"""Design system documentation, served at /design/.

Two kinds of page:

- Markdown pages, one file each under content/. The front matter gives the
  title, the description and, optionally, an order. A folder lists its own
  pages, so adding a page means adding a file and nothing else. The body is
  plain Markdown: no template syntax runs in it.
- HTML pages, in templates/design_system/pages/: the tokens page and the
  demos. Each has its own route, and DEMOS below lists the demos.
"""

import json
import math
import re
from functools import lru_cache, wraps
from pathlib import Path

import markdown
import yaml
from django.conf import settings
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import resolve, reverse
from django.utils.safestring import mark_safe
from wagtailcache.cache import nocache_page

APP_DIR = Path(__file__).resolve().parent
CONTENT_DIR = APP_DIR / "content"
DATA_DIR = APP_DIR / "data"
TOKENS_FILE = DATA_DIR / "tokens.json"
PAGES = "design_system/pages"
MARKDOWN_EXTENSIONS = ["attr_list", "fenced_code", "tables", "toc"]

# Every demo, in the order the demos index lists them. Each is a template,
# templates/design_system/pages/demos/<slug>.html.
DEMOS = {
    "components": (
        "Components",
        "A Library page built from as many of the system's components as it "
        "can use naturally, each labelled with its class.",
    ),
    "typography": (
        "A History of the Book",
        "Every typography element in continuous prose, each labelled with "
        "the element it shows.",
    ),
    "layouts": (
        "Page Layouts",
        "The three standard page layouts, rendered at full page width.",
    ),
    "database-finder": (
        "Database Finder",
        "A copy of the LibGuides A–Z database list, styled by the LibApps "
        "stylesheet, for checking that stylesheet against Springshare's markup.",
    ),
}


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
    its folder's page, so it has no URL of its own; page() redirects to the
    folder's.
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
        "is_folder": is_folder,
        "has_source": path is not None,
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


def render_body(body):
    if not body.strip():
        return ""
    return mark_safe(markdown.markdown(body, extensions=MARKDOWN_EXTENSIONS))


def render_page(request, template, section, context):
    """Renders a page with what the layout needs for its header and breadcrumbs.

    `section` is the first part of the page's path, which the header marks.
    """
    context["section"] = section
    context["sections"] = [item for item in children("") if item["is_folder"]]
    return render(request, template, context)


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
    """The .md URL of a page's source: its URL with the slash swapped for .md.

    The home page's would fall outside /design/, so it is /design/index.md.
    """
    slug = item["slug"] or "index"
    return reverse("design_system:markdown", kwargs={"slug": slug})


@design_view
def markdown_source(request, slug):
    path, _ = locate("" if slug == "index" else slug)
    if not path:
        raise Http404
    source = parse(path)[2]
    return HttpResponse(source, content_type="text/markdown; charset=utf-8")


@design_view
def page(request, slug=""):
    slug = slug or ""
    parent, _, name = slug.rpartition("/")
    if name == "index":
        return redirect(page_url(parent), permanent=True)
    path, is_folder = locate(slug)
    body = parse(path)[1] if path else ""
    context = {
        "page": entry(slug),
        "content": render_body(body),
        "children": children(slug) if is_folder else [],
        "breadcrumbs": breadcrumbs(slug),
    }
    section = slug.split("/")[0]
    return render_page(request, "design_system/page.html", section, context)


def html_page(slug, url, title, description):
    """The `page` of an HTML page, as entry() gives a Markdown page's."""
    return {"slug": slug, "url": url, "title": title, "description": description}


@design_view
def tokens(request):
    page = html_page(
        "tokens",
        reverse("design_system:tokens"),
        "Tokens and Classes",
        "Every design token and documented class, with its CSS variable, SCSS "
        "variable and value. Generated from the stylesheets.",
    )
    context = {"page": page, "breadcrumbs": [page], "tokens": load_tokens()}
    return render_page(request, f"{PAGES}/tokens.html", "tokens", context)


def demos_page():
    return html_page(
        "demos",
        reverse("design_system:demos"),
        "Demos",
        "Complete pages rendered with the design system, to show it in place "
        "and to check it visually.",
    )


def demo_page(slug):
    title, description = DEMOS[slug]
    url = reverse("design_system:demo", kwargs={"slug": slug})
    return html_page(f"demos/{slug}", url, title, description)


@design_view
def demos(request):
    page = demos_page()
    context = {
        "page": page,
        "breadcrumbs": [page],
        "demos": [demo_page(slug) for slug in DEMOS],
    }
    return render_page(request, f"{PAGES}/demos/index.html", "demos", context)


@design_view
def demo(request, slug):
    if slug not in DEMOS:
        raise Http404
    page = demo_page(slug)
    context = {"page": page, "breadcrumbs": [demos_page(), page]}
    return render_page(request, f"{PAGES}/demos/{slug}.html", "demos", context)


@design_view
def tokens_json(request):
    tokens = json.loads(TOKENS_FILE.read_text(encoding="utf-8"))
    # When to use each section's tokens, which the token rows do not repeat.
    guidance = [
        {"tab": table["label"], "section": section["label"], "text": text}
        for table in tokens["tables"]
        for section in table["sections"]
        if (text := section.get("guidance"))
    ]
    return JsonResponse(
        {"tokens": tokens["all"], "classes": tokens["classes"], "guidance": guidance}
    )


def _walk(items):
    for item in items:
        yield item
        yield from _walk(item.get("children", []))


@design_view
def llms_txt(request):
    """Discovery index for agents (https://llmstxt.org), built from content/.

    It links each page's Markdown source. The HTML pages, the tokens page and
    the demos, are left out: what they show is in tokens.json and the prose.
    """
    absolute = request.build_absolute_uri

    def link(item):
        return absolute(markdown_url(item) if item["has_source"] else item["url"])

    home = parse(CONTENT_DIR / "index.md")[0]
    # The introduction is written in content/implementation/index.md, the
    # entry point for people building with the system, with site-relative links.
    builders = parse(CONTENT_DIR / "implementation" / "index.md")[0]
    intro = re.sub(
        r"\]\((/[^)]*)\)", lambda m: f"]({absolute(m[1])})", builders["llms"].strip()
    )
    lines = [f"# {home['title']}", "", f"> {home['description']}", "", intro]
    for section in children(""):
        if not section["is_folder"]:
            continue
        lines += ["", f"## [{section['title']}]({link(section)})", ""]
        for item in _walk(section["children"]):
            description = f": {item['description']}" if item["description"] else ""
            lines.append(f"- [{item['title']}]({link(item)}){description}")
    return HttpResponse(
        "\n".join(lines) + "\n", content_type="text/plain; charset=utf-8"
    )
