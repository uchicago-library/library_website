from django.core.cache import cache
from django.http import HttpRequest
from django.test import TestCase
from django.urls import clear_url_caches
from wagtailcache.cache import clear_cache

from alerts.models import AlertPage
from base.tests import add_generic_request_meta_fields, boiler_plate


class TestAlertPageOnDesignSystemBase(TestCase):
    """
    The alert page is the first page type on the Bootstrap 5 base
    (#1112), so it checks that base: the design system's assets, none
    of Bootstrap 3's, and the hooks other scripts rely on.
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

    def serve(self):
        request = HttpRequest()
        add_generic_request_meta_fields(request)
        return self.alert.serve(request)

    def test_loads_the_design_system(self):
        response = self.serve()
        self.assertContains(response, "design_system/css/main.css")
        self.assertContains(response, "design_system/js/bootstrap.bundle.min.js")
        self.assertContains(response, "font-awesome/6.5.2")

    def test_loads_no_bootstrap_3(self):
        response = self.serve()
        self.assertNotContains(response, "base/css/bootstrap.min.css")
        self.assertNotContains(response, "base/js/bootstrap.min.js")
        self.assertNotContains(response, "font-awesome-4.6.3")

    def test_has_the_site_chrome(self):
        response = self.serve()
        self.assertContains(response, 'href="#content"')
        self.assertContains(response, '<main id="content"', count=1)
        self.assertContains(response, 'id="global-navbar"', count=1)
        # voc-button.js adds its feedback link to this list
        self.assertContains(response, 'aria-labelledby="contact_label"', count=1)

    def test_renders_the_page_content(self):
        response = self.serve()
        self.assertContains(response, "<h1>Red Alert</h1>", html=True)
        self.assertContains(response, "All hands to battle stations.")
