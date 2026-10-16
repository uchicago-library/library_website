import json
import re

from django.test import TestCase
from django.urls import reverse

from . import views

INTERNAL_LINK = re.compile(r'href="(/design/[^"#?]*)')


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
