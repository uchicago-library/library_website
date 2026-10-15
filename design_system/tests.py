import json
import re

from django.test import TestCase

from . import views

INTERNAL_LINK = re.compile(r'href="(/design/[^"#?]*)')


class DesignSystemTest(TestCase):
    """Checks every page found in design_system/content/, so none is named here."""

    def setUp(self):
        # Pass the site's Turnstile check whether or not it is enabled.
        session = self.client.session
        session["turnstile_passed"] = True
        session.save()
        self.pages = [views.entry("")] + list(views._walk(views.children("")))

    def get(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, url)
        self.assertIn("noindex", response["X-Robots-Tag"], url)
        return response.content.decode()

    def test_every_page_and_its_source_render(self):
        for page in self.pages:
            with self.subTest(url=page["url"]):
                self.get(page["url"])
                if views.locate(page["slug"])[0]:
                    self.get(views.markdown_url(page))

    def test_internal_links_resolve(self):
        checked = set()
        for page in self.pages:
            for href in set(INTERNAL_LINK.findall(self.get(page["url"]))) - checked:
                checked.add(href)
                with self.subTest(page=page["url"], href=href):
                    self.get(href)

    def test_llms_txt_lists_every_page(self):
        text = self.get("/design/llms.txt")
        for page in self.pages[1:]:
            with self.subTest(url=page["url"]):
                self.assertIn(page["url"].rstrip("/"), text)

    def test_tokens_json(self):
        data = json.loads(self.get("/design/tokens.json"))
        self.assertTrue(data["tokens"])
        self.assertTrue(data["classes"])
