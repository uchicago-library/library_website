import json
import re

from django.conf import settings
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from . import views
from .urls import SEGMENT

INTERNAL_LINK = re.compile(r'href="(/design/[^"#?]*)')
SCRIPT = re.compile(r"<script\b([^>]*)>(.*?)</script>", re.S | re.I)
INLINE_HANDLER = re.compile(r"<[^>]*\son[a-z]+\s*=", re.I)
JAVASCRIPT_URL = re.compile(r"""<[^>]*=\s*["']?\s*javascript:""", re.I)


class ContentFilesTest(SimpleTestCase):
    """Every file in content/ is one the views can read.

    A bad file breaks more than its own page: its folder's listing, llms.txt
    and the walk in DesignSystemTest.setUp. These checks name the file and the
    problem instead.
    """

    def test_every_content_file_is_valid(self):
        for path in views.CONTENT_DIR.rglob("*"):
            if not (path.is_dir() or path.suffix == ".md"):
                continue
            name = path.relative_to(views.CONTENT_DIR).as_posix()
            with self.subTest(file=name):
                stem = path.name if path.is_dir() else path.stem
                self.assertRegex(
                    stem,
                    rf"^{SEGMENT}$",
                    "names are letters, digits, hyphens and underscores only",
                )
                if path.is_dir():
                    continue
                source = path.read_text(encoding="utf-8").replace("\r\n", "\n")
                if source.startswith("---\n"):
                    self.assertGreaterEqual(
                        source.count("---\n"), 2, "front matter is never closed"
                    )
                meta = views.parse(path)[0]
                self.assertIsInstance(meta, dict, "front matter is not a mapping")
                order = meta.get("order", 0)
                self.assertIsInstance(order, (int, float), "order is not a number")

    def test_llms_txt_front_matter(self):
        home = views.parse(views.CONTENT_DIR / "index.md")[0]
        builders = views.parse(views.CONTENT_DIR / "implementation" / "index.md")[0]
        for meta, key in [(home, "title"), (home, "description"), (builders, "llms")]:
            with self.subTest(key=key):
                self.assertTrue(meta.get(key), f"{key} is missing")


class DesignSystemTest(TestCase):
    """Checks every page in content/ and in views.DEMOS, so none is named here."""

    def setUp(self):
        # Pass the site's Turnstile check whether or not it is enabled.
        session = self.client.session
        session["turnstile_passed"] = True
        session.save()
        self.pages = [views.entry("")] + list(views._walk(views.children("")))
        self.html_pages = [
            reverse("design_system:tokens"),
            reverse("design_system:demos"),
        ] + [views.demo_page(slug)["url"] for slug in views.DEMOS]

    def get(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, url)
        self.assertIn("noindex", response["X-Robots-Tag"], url)
        return response.content.decode()

    def test_every_page_and_its_source_render(self):
        for page in self.pages:
            with self.subTest(url=page["url"]):
                self.get(page["url"])
                if page["has_source"]:
                    self.get(views.markdown_url(page))
        for url in self.html_pages:
            with self.subTest(url=url):
                self.get(url)

    def test_internal_links_resolve(self):
        checked = set()
        for url in [page["url"] for page in self.pages] + self.html_pages:
            for href in set(INTERNAL_LINK.findall(self.get(url))) - checked:
                checked.add(href)
                with self.subTest(page=url, href=href):
                    self.get(href)

    def test_no_page_runs_inline_or_off_site_script(self):
        # Pages are served from the site's own origin, so script on them runs
        # with a signed-in staff member's session. See Styling Springshare
        # Pages for why the database finder's copy of Springshare's is removed.
        for url in [page["url"] for page in self.pages] + self.html_pages:
            html = self.get(url)
            with self.subTest(url=url):
                for attrs, body in SCRIPT.findall(html):
                    src = re.search(r'\bsrc="([^"]*)"', attrs)
                    self.assertTrue(src, f"inline <script>: {body.strip()[:60]}")
                    self.assertTrue(
                        src[1].startswith(settings.STATIC_URL), f"off-site {src[1]}"
                    )
                self.assertNotRegex(html, INLINE_HANDLER)
                self.assertNotRegex(html, JAVASCRIPT_URL)

    def test_llms_txt_lists_every_page(self):
        text = self.get("/design/llms.txt")
        for page in self.pages[1:]:
            with self.subTest(url=page["url"]):
                self.assertIn(page["url"].rstrip("/"), text)
        for url in re.findall(r"\]\(http://testserver(/[^)]*)\)", text):
            with self.subTest(link=url):
                self.get(url)

    def test_markdown_is_served_as_written(self):
        # Template syntax in a page body would reach readers unrun.
        for page in self.pages:
            if page["has_source"]:
                with self.subTest(url=page["url"]):
                    self.assertNotRegex(self.get(views.markdown_url(page)), r"{%|{{")

    def test_missing_page(self):
        for url in [
            "/design/no-such-page/",
            "/design/foundations/index.md",
            "/design/demos/no-such-demo/",
        ]:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(response, "Page Not Found", status_code=404)

    def test_index_redirects_to_its_folder(self):
        for url, target in [
            ("/design/index/", "/design/"),
            ("/design/foundations/index/", "/design/foundations/"),
        ]:
            with self.subTest(url=url):
                self.assertRedirects(self.client.get(url), target, status_code=301)

    def test_tokens_json(self):
        data = json.loads(self.get("/design/tokens.json"))
        self.assertTrue(data["tokens"])
        self.assertTrue(data["classes"])
        self.assertTrue(all(item["text"] for item in data["guidance"]))
