"""Tests for mylib_dashboard.utils."""

from django.test import RequestFactory, TestCase, override_settings

from mylib_dashboard.utils import get_current_cnetid, get_current_email


class TestGetCurrentCnetid(TestCase):
    """Tests for get_current_cnetid()."""

    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()

    @override_settings(DEBUG=True, MYLIB_DEV_USERNAME="devuser")
    def test_returns_dev_username_when_debug_and_configured(self):
        request = self.factory.get("/")
        self.assertEqual(get_current_cnetid(request), "devuser")

    @override_settings(DEBUG=False, MYLIB_DEV_USERNAME="devuser")
    def test_returns_meta_uid_when_not_debug(self):
        request = self.factory.get("/")
        request.META["uid"] = "testuser"
        self.assertEqual(get_current_cnetid(request), "testuser")

    @override_settings(DEBUG=False)
    def test_returns_none_when_no_uid_in_meta(self):
        request = self.factory.get("/")
        self.assertIsNone(get_current_cnetid(request))

    @override_settings(DEBUG=False, MYLIB_DEV_USERNAME="devuser")
    def test_ignores_dev_username_when_not_debug(self):
        request = self.factory.get("/")
        self.assertIsNone(get_current_cnetid(request))


class TestGetCurrentEmail(TestCase):
    """Tests for get_current_email()."""

    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()

    @override_settings(DEBUG=True, MYLIB_DEV_EMAIL="dev@example.com")
    def test_returns_dev_email_when_debug_and_configured(self):
        request = self.factory.get("/")
        self.assertEqual(get_current_email(request), "dev@example.com")

    @override_settings(DEBUG=False, MYLIB_DEV_EMAIL="dev@example.com")
    def test_returns_meta_mail_when_not_debug(self):
        request = self.factory.get("/")
        request.META["mail"] = "user@example.com"
        self.assertEqual(get_current_email(request), "user@example.com")

    @override_settings(DEBUG=False)
    def test_returns_none_when_no_mail_in_meta(self):
        request = self.factory.get("/")
        self.assertIsNone(get_current_email(request))

    @override_settings(DEBUG=False, MYLIB_DEV_EMAIL="dev@example.com")
    def test_ignores_dev_email_when_not_debug(self):
        request = self.factory.get("/")
        self.assertIsNone(get_current_email(request))
