from django.core.cache import cache
from django.http import HttpRequest
from django.test import TestCase
from django.urls import clear_url_caches
from wagtailcache.cache import clear_cache

from alerts.models import AlertPage
from base.tests import add_generic_request_meta_fields, boiler_plate


class TestAlertPage(TestCase):
    """
    The alert page renders on the Bootstrap 5 base. The base itself is
    tested in base/tests.py (TestDesignSystemBase).
    """

    @classmethod
    def setUpTestData(cls):
        boiler_plate(cls)
        cls.alert = AlertPage(
            title="Red Alert",
            banner_message="<p>Shields up.</p>",
            more_info="<p>All hands to battle stations.</p>",
            page_maintainer=cls.staff,
            editor=cls.staff,
            content_specialist=cls.staff,
            unit=cls.unit,
        )
        cls.homepage.add_child(instance=cls.alert)

    def tearDown(self):
        clear_url_caches()
        cache.clear()
        clear_cache()

    def test_renders_the_page_content(self):
        request = HttpRequest()
        add_generic_request_meta_fields(request)
        response = self.alert.serve(request)
        self.assertContains(response, "<h1>Red Alert</h1>", html=True)
        self.assertContains(response, "All hands to battle stations.")
