"""Tests for mylib_dashboard.models."""

from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings

from mylib_dashboard.models import MyLibDashboardPage


class TestMyLibDashboardPage(TestCase):
    """Tests for the MyLibDashboardPage model."""

    def test_field_defaults(self):
        page = MyLibDashboardPage()
        self.assertIn("Auto-renewal", page.auto_renewal_notice)
        self.assertEqual(page.max_items_per_card, 0)
        self.assertIn("catalog.lib.uchicago.edu", page.catalog_account_url)
        self.assertIn("lib.uchicago.edu", page.accounts_faq_url)

    def test_subpage_types_empty(self):
        self.assertEqual(MyLibDashboardPage.subpage_types, [])

    @override_settings(
        ILLIAD_WEB_BASE_URL="https://illiad.example.com",
        LIBCAL_WEB_URL="https://libcal.example.com",
    )
    def test_get_context_adds_urls(self):
        page = MyLibDashboardPage()
        request = MagicMock()

        # Provide a minimal mock for super().get_context() chain
        with _patch_super_context(page, request):
            result = page.get_context(request)

        self.assertEqual(result["illiad_web_url"], "https://illiad.example.com")
        self.assertEqual(result["libcal_web_url"], "https://libcal.example.com")

    @override_settings(ILLIAD_WEB_BASE_URL="", LIBCAL_WEB_URL="")
    def test_get_context_handles_missing_settings(self):
        page = MyLibDashboardPage()
        request = MagicMock()

        with _patch_super_context(page, request):
            result = page.get_context(request)

        self.assertEqual(result["illiad_web_url"], "")
        self.assertEqual(result["libcal_web_url"], "")

    def test_verbose_name(self):
        self.assertEqual(MyLibDashboardPage._meta.verbose_name, "MyLib Dashboard Page")
        self.assertEqual(
            MyLibDashboardPage._meta.verbose_name_plural, "MyLib Dashboard Pages"
        )


class _patch_super_context:
    """Context manager that patches the parent class get_context to return a plain dict."""

    def __init__(self, page, request):
        self.page = page
        self.request = request
        self._patcher = None

    def __enter__(self):
        # Patch the parent class's get_context to avoid Wagtail page tree lookups
        self._patcher = patch(
            "mylib_dashboard.models.PublicBasePage.get_context",
            return_value={},
        )
        self._patcher.start()
        return {}

    def __exit__(self, *args):
        self._patcher.stop()
