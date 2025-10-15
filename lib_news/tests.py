from ask_a_librarian.models import AskPage
from django.core.cache import cache
from django.test import Client, RequestFactory, TestCase
from django.urls import clear_url_caches
from public.models import LocationPage
from staff.models import StaffPage
from units.models import UnitPage
from wagtail.models import Page, Site
from wagtailcache.cache import clear_cache

from lib_news.models import LibNewsIndexPage, LibNewsPage, PublicNewsCategories


class test_lib_news_pages_and_categories(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create the homepage (runs once for all tests in this class)
        root = Page.objects.get(path='0001')
        cls.homepage = Page(slug='starfleet-welcome', title='Welcome to the Federation')
        root.add_child(instance=cls.homepage)

        # Create a site and associate the homepage with it
        cls.hostname = 'final-frontier'
        cls.site = Site.objects.create(
            hostname=cls.hostname,
            is_default_site=True,
            port=80,
            root_page=cls.homepage,
            site_name='test site',
        )

        # Necessary pages
        cls.staff = StaffPage(
            title='Jean-Luc Picard',
            cnetid='picard',
            position_title='Captain of the USS Enterprise',
        )
        cls.homepage.add_child(instance=cls.staff)

        cls.unit = UnitPage(
            title='USS Enterprise (NCC-1701-D)',
            page_maintainer=cls.staff,
            editor=cls.staff,
            display_in_dropdown=True,
        )
        cls.homepage.add_child(instance=cls.unit)

        cls.ask_page = AskPage(
            title='Ask a Betazoid (or don\'t)',
            page_maintainer=cls.staff,
            editor=cls.staff,
            content_specialist=cls.staff,
            unit=cls.unit,
        )
        cls.homepage.add_child(instance=cls.ask_page)

        cls.building = LocationPage(
            title='Deep Space 9',
            is_building=True,
            short_description='A space station orbiting Bajor.',
            long_description='A space station orbiting Bajor\
            that was called Terok Nor during the occupation.',
            page_maintainer=cls.staff,
            editor=cls.staff,
            content_specialist=cls.staff,
            libcal_library_id=1357,
            unit=cls.unit,
        )
        cls.homepage.add_child(instance=cls.building)

        # Set location property on UnitPage already created
        cls.unit.location = cls.building
        cls.unit.save()

        cls.news_homepage = LibNewsIndexPage(
            title='Starfleet News',
            page_maintainer=cls.staff,
            editor=cls.staff,
            content_specialist=cls.staff,
            unit=cls.unit,
            slug='starfleet-news',
        )
        cls.homepage.add_child(instance=cls.news_homepage)

        cls.news_article = LibNewsPage(
            title='Borg Attack!',
            page_maintainer=cls.staff,
            editor=cls.staff,
            content_specialist=cls.staff,
            unit=cls.unit,
            slug='borg-attack',
        )
        cls.news_homepage.add_child(instance=cls.news_article)
        PublicNewsCategories.objects.create(text='Picard').save()
        PublicNewsCategories.objects.create(text='Borg').save()
        PublicNewsCategories.objects.create(text='Alpha Quadrant').save()
        cls.news_article.save()
        cls.news_homepage.save()

    def setUp(self):
        # Delete the default localhost site created by Wagtail migrations
        # to prevent conflicts with our test site
        Site.objects.filter(hostname='localhost').delete()

        # Clear cache before each test
        # This ensures Wagtail doesn't use stale cached references
        clear_url_caches()
        cache.clear()
        clear_cache()

        # Create per-test objects
        self.factory = RequestFactory()
        self.client = Client()

    def tearDown(self):
        # Clear cache after each test
        clear_url_caches()
        cache.clear()
        clear_cache()

    def test_get_alpha_cats_with_categories(self):
        cats = self.news_homepage.get_alpha_cats()
        self.assertEqual(cats[0], 'Alpha Quadrant')
        self.assertEqual(cats[1], 'Borg')
        self.assertEqual(cats[2], 'Picard')

    def test_get_alpha_cats_without_categories(self):
        PublicNewsCategories.objects.all().delete()
        cats = self.news_homepage.get_alpha_cats()
        self.assertEqual(cats, [])

    def test_generic_news_article_page_routing(self):
        # In parallel tests, get_url_parts() can return None
        # Use the expected path directly based on the page structure
        url = '/starfleet-news/borg-attack/'
        response = self.client.get(url, HTTP_HOST=self.hostname)
        self.assertEqual(response.status_code, 200)

    def test_news_article_page_routing_to_category_listing(self):
        PublicNewsCategories.objects.create(text='Borg').save()
        url = '/starfleet-news/category/borg/'
        response = self.client.get(url, HTTP_HOST=self.hostname)
        self.assertEqual(response.status_code, 200)

    def test_404_response(self):
        url = '/starfleet-news/adsfasdf/'
        response = self.client.get(url, HTTP_HOST=self.hostname)
        self.assertEqual(response.status_code, 404)
