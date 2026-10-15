import json
import re

from django.test import TestCase

from . import views

INTERNAL_LINK = re.compile(r'href="(/design/[^"#?]*)')


class DesignSystemPagesTest(TestCase):
    """Every page under design_system/content/ renders and links correctly."""

    def setUp(self):
        # Pass the site's Turnstile check whether or not it is enabled.
        session = self.client.session
        session["turnstile_passed"] = True
        session.save()

    def pages(self):
        return [views.entry("")] + list(views._walk(views.children("")))

    def test_every_page_renders(self):
        for page in self.pages():
            with self.subTest(url=page["url"]):
                response = self.client.get(page["url"])
                self.assertEqual(response.status_code, 200)

    def test_internal_links_resolve(self):
        checked = {}
        for page in self.pages():
            html = self.client.get(page["url"]).content.decode()
            for href in set(INTERNAL_LINK.findall(html)):
                if href not in checked:
                    checked[href] = self.client.get(href).status_code
                with self.subTest(page=page["url"], href=href):
                    self.assertEqual(checked[href], 200)

    def test_prose_pages_serve_their_markdown(self):
        page = views.entry("guidelines/copywriting")
        response = self.client.get(page["url"], {"format": "md"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response["Content-Type"].startswith("text/markdown"))
        self.assertTrue(response.content.decode().startswith("---\n"))

    def test_folders_list_their_pages(self):
        html = self.client.get(views.page_url("guidelines")).content.decode()
        for child in views.children("guidelines"):
            self.assertIn(f'href="{child["url"]}"', html)

    def test_unknown_page_is_404(self):
        self.assertEqual(self.client.get("/design/no-such-page/").status_code, 404)

    def test_llms_txt_lists_every_page(self):
        response = self.client.get("/design/llms.txt")
        self.assertEqual(response.status_code, 200)
        text = response.content.decode()
        for page in views._walk(views.children("")):
            with self.subTest(url=page["url"]):
                self.assertIn(page["url"], text)

    def test_tokens_json(self):
        response = self.client.get("/design/tokens.json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data["tokens"])
        self.assertTrue(data["classes"])

    def test_token_tables_render_notes_as_markdown(self):
        html = self.client.get(views.page_url(views.TOKEN_TABLES_SLUG)).content.decode()
        self.assertIn('class="token-table__notes"', html)
        self.assertIn("<code>", html)
