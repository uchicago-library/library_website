from ask_a_librarian.models import AskPage
from django.test import Client, RequestFactory, TestCase
from lib_news.models import LibNewsIndexPage, LibNewsPage, PublicNewsCategories
from public.models import LocationPage
from staff.models import StaffPage
from units.models import UnitPage
from wagtail.models import Page, Site


class test_lib_news_pages_and_categories(TestCase):

    def setUp(self):
        # Create the homepage
        """try:
            self.homepage = Page.objects.get(path='00010001')
        except (Page.DoesNotExist):
            root = Page.objects.create(
                depth=1, path='0001', slug='root', title='Root'
            )
            self.homepage = Page(
                path='00010001', slug='welcome', title='Welcome'
            )
            root.add_child(instance=self.homepage)"""
        root = Page.objects.get(path='0001')
        self.homepage = Page(
            slug='starfleet-welcome', title='Welcome to the Federation'
        )
        root.add_child(instance=self.homepage)

        # Create a site and associate the homepage with it
        self.site = Site.objects.create(
            hostname='final-frontier',
            is_default_site=True,
            port=80,
            root_page=self.homepage,
            site_name='test site'
        )

        # Necessary pages
        self.staff = StaffPage(
            title='Jean-Luc Picard',
            cnetid='picard',
            position_title='Captain of the USS Enterprise'
        )
        self.homepage.add_child(instance=self.staff)

        self.unit = UnitPage(
            title='USS Enterprise (NCC-1701-D)',
            page_maintainer=self.staff,
            editor=self.staff,
            display_in_dropdown=True
        )
        self.homepage.add_child(instance=self.unit)

        self.ask_page = AskPage(
            title='Ask a Betazoid (or don\'t)',
            page_maintainer=self.staff,
            editor=self.staff,
            content_specialist=self.staff,
            unit=self.unit
        )
        self.homepage.add_child(instance=self.ask_page)

        self.building = LocationPage(
            title='Deep Space 9',
            is_building=True,
            short_description='A space station orbiting Bajor.',
            long_description='A space station orbiting Bajor\
            that was called Terok Nor during the occupation.',
            page_maintainer=self.staff,
            editor=self.staff,
            content_specialist=self.staff,
            libcal_library_id=1357,
            unit=self.unit
        )
        self.homepage.add_child(instance=self.building)

        # Set location property on UnitPage already created
        self.unit.location = self.building
        self.unit.save()

        self.news_homepage = LibNewsIndexPage(
            title='Starfleet News',
            page_maintainer=self.staff,
            editor=self.staff,
            content_specialist=self.staff,
            unit=self.unit,
            slug='starfleet-news',
        )
        self.homepage.add_child(instance=self.news_homepage)

        self.news_article = LibNewsPage(
            title='Borg Attack!',
            page_maintainer=self.staff,
            editor=self.staff,
            content_specialist=self.staff,
            unit=self.unit,
            slug='borg-attack',
        )
        self.news_homepage.add_child(instance=self.news_article)

        self.factory = RequestFactory()
        self.client = Client()

    def tearDown(self):
        self.site.delete()

    def test_get_alpha_cats_with_categories(self):
        PublicNewsCategories.objects.create(text='Picard').save()
        PublicNewsCategories.objects.create(text='Borg').save()
        PublicNewsCategories.objects.create(text='Alpha Quadrant').save()
        cats = self.news_homepage.get_alpha_cats()
        self.assertEqual(cats[0], 'Alpha Quadrant')
        self.assertEqual(cats[1], 'Borg')
        self.assertEqual(cats[2], 'Picard')

    def test_get_alpha_cats_without_categories(self):
        cats = self.news_homepage.get_alpha_cats()
        self.assertEqual(cats, [])

    def test_visit_to_news_article_page(self):
        url = LibNewsPage.objects.live().first().url
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_generic_news_article_page_routing(self):
        url = self.news_article.url
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_news_article_page_routing_to_category_listing(self):
        url = '/starfleet-news/category/borg/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_non_existing_sub_url_on_article_page(self):
        url = '/starfleet-news/adsfasdf/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
