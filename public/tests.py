import warnings

import requests
from base.tests import add_generic_request_meta_fields, boiler_plate
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.http import HttpRequest
from django.test import SimpleTestCase, TestCase
from django.urls import clear_url_caches, reverse
from elasticsearch import ElasticsearchWarning
from library_website.settings import IDRESOLVE_URL
from results.views import main_search_query, pages_to_exclude
from wagtail.models import Page
from wagtailcache.cache import clear_cache

from public.utils import doi_lookup, doi_lookup_base_url, mk_url

example_doi1 = "10.1007/s11050-007-9022-y"
example_doi2 = "10.1017/S0960129518000324"
bad_url = "https://not-an-actual-api-I-just-made-it-up.com?"
bad_doi = "NOT_A_DOI"


class IdresolveTest(SimpleTestCase):

    fixtures = ['test.json']

    def test_idresolve_is_up(self):
        """
        check that idresolve returns a response when given a valid DOI and
        base URL

        """
        assert doi_lookup(example_doi1) is not None
        assert doi_lookup(example_doi2) is not None

    def test_good_url_no_exception(self):
        """
        ensure no exception gets thrown when trying to connect to
        idresolve at the correct URL

        """
        try:
            doi_lookup(example_doi1)
            doi_lookup(example_doi2)
        except requests.ConnectionError:
            self.fail("Idresolve service is not up.")

    def test_bad_url_no_exception(self):
        """
        ensure no exception gets thrown when trying to connect to
        idresolve at the wrong URL
        """
        try:
            doi_lookup_base_url(example_doi1, bad_url)
            doi_lookup_base_url(example_doi2, bad_url)
        except requests.ConnectionError as exception:
            self.fail("public.utils doi_lookup raised %s"
                      % str(exception)
                      )

    def test_bad_doi_returns_none(self):
        """
        ensure a request to idresolve with an ill-formed DOI fails
        gracefully (i.e. returns None)

        """
        resp = doi_lookup_base_url(bad_doi, IDRESOLVE_URL)
        assert resp is None

    def test_doi_good_status_code(self):
        """
        check that a good URL and DOI return a response with a 200 status
        code

        """
        resp1 = requests.get(mk_url(example_doi1, IDRESOLVE_URL))
        resp2 = requests.get(mk_url(example_doi2, IDRESOLVE_URL))
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(resp2.status_code, 200)

    def test_valid_idresolve_url(self):
        """
        check that idresolve returned a well-formed URL that the Wagtail
        app can perform a redirect to

        """
        validate = URLValidator()
        result1 = doi_lookup(example_doi1)
        result2 = doi_lookup(example_doi1)
        try:
            validate(result1[:-1])
            validate(result2[:-1])
        except ValidationError:
            self.fail("Idresolve not returning valid SFX url.")


class TestStandardPageExcludeFields(TestCase):
    def setUp(self):
        # Create necessary pages
        boiler_plate(self)
        self.meta_tag = '<meta name="robots" content="noindex" />'
        warnings.filterwarnings("ignore", category=ElasticsearchWarning)

    def tearDown(self):
        clear_url_caches()
        cache.clear()
        clear_cache()

    def test_no_robots_meta_tag_on_a_default_page(self):
        request = HttpRequest()
        add_generic_request_meta_fields(request)
        response = self.page.serve(request)
        self.assertNotContains(response, self.meta_tag)

    def test_page_excluded_from_search_engines_has_meta_tag(self):
        self.page.exclude_from_search_engines = True
        self.page.save()
        request = HttpRequest()
        add_generic_request_meta_fields(request)
        response = self.page.serve(request)
        self.assertContains(response, self.meta_tag)

    def test_normal_page_shows_in_search(self):
        self.page.save_revision().publish()
        self.assertNotIn(self.page, pages_to_exclude())
        self.assertIn(
            Page.objects.all().get(id=self.page.id),
            main_search_query(Page.objects.live()),
        )

    def test_page_excluded_from_site_search_does_not_show_in_search(self):
        self.page.exclude_from_site_search = True
        self.page.save_revision().publish()
        self.assertIn(self.page, pages_to_exclude())
        self.assertNotIn(
            Page.objects.live().get(id=self.page.id),
            main_search_query(Page.objects.live()),
        )


class TestStandardPageSitemapExcludeFieldFalse(TestCase):
    def setUp(self):
        # Create necessary pages
        boiler_plate(self)

    def tearDown(self):
        clear_url_caches()
        cache.clear()
        clear_cache()

    def test_normal_page_shows_in_sitemap_xml(self):
        self.page.exclude_from_sitemap_xml = False
        self.page.save_revision().publish()
        response = self.client.get(reverse('inventory'))
        sitemap_url = self.page.get_sitemap_urls(response)
        self.assertEqual(
            sitemap_url[0]['location'],
            'http://starfleet-academy.com/the-great-link-test/',
        )
        self.assertContains(response, 'the-great-link-test')


class TestStandardPageSitemapExcludeFieldTrue(TestCase):
    def setUp(self):
        # Create necessary pages
        boiler_plate(self)

    def tearDown(self):
        clear_url_caches()
        cache.clear()
        clear_cache()

    def test_page_excluded_from_sitemap_xml_not_in_sitemap_xml(self):
        self.page.exclude_from_sitemap_xml = True
        self.page.save_revision().publish()
        response = self.client.get(reverse('inventory'))
        sitemap_url = self.page.get_sitemap_urls(response)
        self.assertEqual(sitemap_url, [])
        self.assertNotContains(response, 'the-great-link-test')
