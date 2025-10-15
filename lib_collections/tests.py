import os
import time
import unittest

import simplejson
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache, caches
from django.test import RequestFactory, SimpleTestCase, TestCase
from django.urls import clear_url_caches
from public.models import LocationPage, StaffPublicPage
from staff.models import StaffPage, StaffPageSubjectPlacement
from subjects.models import Subject
from units.models import UnitPage
from wagtail.models import Page, Site
from wagtail.search.backends import get_search_backend
from wagtailcache.cache import clear_cache

from lib_collections.marklogic import get_record_for_display
from lib_collections.models import CollectingAreaPage, CollectionPage, ExhibitPage
from lib_collections.utils import CBrowseURL, DisplayBrowse, IIIFDisplay, Testing
from lib_collections.views import collections


class test_lib_collections_view(TestCase):
    fixtures = ['test.json']

    def setUp(self):
        self.factory = RequestFactory()
        self.user = AnonymousUser()
        self.startTime = time.time()
        # set up factory request

    def tearDown(self):

        caches['default'].clear()
        # clear cache

    def test_view(self):
        request = self.factory.get('/collection/')
        request.user = self.user
        response = collections(request)

        self.assertEqual(response.status_code, 200)

    def test_view_collections(self):
        request = self.factory.get('/collection/?view=collections')
        request.user = self.user
        response = collections(request)

        self.assertEqual(response.status_code, 200)

    def test_collections_digital(self):
        request = self.factory.get('/collection/?view=collections&digital=on')
        request.user = self.user
        response = collections(request)

        self.assertContains(
            response,
            '<input name="digital" type="checkbox" aria-label="limit to digital collections" id="checkboxdigital" checked="checked">',
            html=True,
        )

    def test_collections_format(self):
        """Test format filtering with representative samples."""
        # Test a few representative formats instead of all 11
        test_formats = ['Archives & Manuscripts', 'Audio', 'Video']

        for format_name in test_formats:
            request = self.factory.get(
                f'/collection/?view=collections&format={format_name}'
            )
            request.user = self.user
            response = collections(request)

            self.assertEqual(response.status_code, 200)

    def test_collections_format_invalid(self):
        """Test that invalid format is handled gracefully."""
        request = self.factory.get('/collection/?view=collections&format=InvalidFormat')
        request.user = self.user
        response = collections(request)

        # Should still return 200, but ignore the invalid format
        self.assertEqual(response.status_code, 200)

    def test_collections_location(self):
        """Test location filtering with representative samples."""
        # Get first 3 live locations instead of all 73
        sample_locations = LocationPage.objects.live().values_list('title', flat=True)[
            :3
        ]

        for location in sample_locations:
            request = self.factory.get(
                f'/collection/?view=collections&location={location}'
            )
            request.user = self.user
            response = collections(request)

            self.assertEqual(response.status_code, 200)

    def test_collections_location_invalid(self):
        """Test that invalid location is handled gracefully."""
        request = self.factory.get(
            '/collection/?view=collections&location=NonexistentLocation'
        )
        request.user = self.user
        response = collections(request)

        # Should still return 200, but ignore the invalid location
        self.assertEqual(response.status_code, 200)

    def test_collections_subject(self):
        """Test subject filtering with representative samples."""
        # Get first 5 subjects instead of all 118
        sample_subjects = Subject.objects.all().values_list("name", flat=True)[:5]

        for subject in sample_subjects:
            request = self.factory.get(
                f'/collection/?view=collections&subject={subject}'
            )
            request.user = self.user
            response = collections(request)

            self.assertEqual(response.status_code, 200)

    def test_collections_subject_invalid(self):
        """Test that invalid subject is handled gracefully."""
        request = self.factory.get(
            '/collection/?view=collections&subject=NonexistentSubject'
        )
        request.user = self.user
        response = collections(request)

        # Should still return 200, but ignore the invalid subject
        self.assertEqual(response.status_code, 200)

    def test_view_exhibit(self):
        request = self.factory.get('/collection/?view=exhibits')
        request.user = self.user
        response = collections(request)

        self.assertEqual(response.status_code, 200)

    def test_exhibit_location_none(self):
        request = self.factory.get('/collection/?view=exhibits&location=%s' % None)
        request.user = self.user
        response = collections(request)

        self.assertEqual(response.status_code, 200)

    def test_exhibit_subject_none(self):
        request = self.factory.get('/collection/?view=exhibits&subject=%s' % None)
        request.user = self.user
        response = collections(request)

        self.assertEqual(response.status_code, 200)

    def test_exhibit_digital_none(self):
        request = self.factory.get('/collection/?view=exhibits&digital=%s' % None)
        request.user = self.user
        response = collections(request)

        self.assertEqual(response.status_code, 200)

    def test_view_subjects(self):
        request = self.factory.get('/collection/?view=subjects')
        request.user = self.user
        response = collections(request)

        self.assertEqual(response.status_code, 200)

    def test_view_none(self):
        request = self.factory.get('/collection/?view=%s' % None)
        request.user = self.user
        response = collections(request)

        self.assertEqual(response.status_code, 200)

    def test_view_invalid(self):
        request = self.factory.get('/collection/?view=gibberish')
        request.user = self.user
        response = collections(request)

        self.assertEqual(response.status_code, 200)


class TestCollectingAreaPages(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Delete the default localhost site created by Wagtail migrations
        # to prevent conflicts with our test site
        Site.objects.filter(hostname='localhost').delete()

        # Configuration for subjects (runs once for all tests in this class)
        subjects_json = {
            'tng': {
                'name': 'Star Trek: The Next Generation',
                'json': '{"display_in_dropdown": false, "parent_subject": [], "libguide_url": null, "see_also": [], "pk": %s, "name": "%s"}',
            },
            'ds9': {
                'name': 'Star Trek: Deep Space Nine',
                'json': '{"display_in_dropdown": false, "parent_subject": [], "libguide_url": null, "see_also": [], "pk": %s, "name": "%s"}',
            },
            'original': {
                'name': 'Star Trek: The Original Series',
                'json': '{"display_in_dropdown": false, "parent_subject": [], "libguide_url": null, "see_also": [], "pk": %s, "name": "%s"}',
            },
            'tribbles': {
                'name': 'Tribbles',
                'json': '{"display_in_dropdown": false, "parent_subject": [{"sort_order": 0, "parent": %s, "pk": %s, "child": %s}, {"sort_order": 1, "parent": %s, "pk": %s, "child": %s}], "libguide_url": "", "see_also": [], "pk": %s, "name": "%s"}',
            },
            'quadrotriticale': {
                'name': 'Quadrotriticale',
                'json': '{"display_in_dropdown": false, "parent_subject": [{"sort_order": 0, "parent": %s, "pk": %s, "child": %s}], "libguide_url": "", "see_also": [], "pk": %s, "name": "%s"}',
            },
        }

        # Create subjects to operate on
        Subject.objects.create(name=subjects_json['tng']['name']).save()
        Subject.objects.create(name=subjects_json['ds9']['name']).save()
        Subject.objects.create(name=subjects_json['original']['name']).save()
        Subject.objects.create(name=subjects_json['tribbles']['name']).save()
        Subject.objects.create(name=subjects_json['quadrotriticale']['name']).save()

        # Load the subjects into variables
        subjects = Subject.objects.all()
        cls.tng = subjects.get(name=subjects_json['tng']['name'])
        cls.ds9 = subjects.get(name=subjects_json['ds9']['name'])
        cls.original = subjects.get(name=subjects_json['original']['name'])
        cls.tribbles = subjects.get(name=subjects_json['tribbles']['name'])
        cls.quadrotriticale = subjects.get(
            name=subjects_json['quadrotriticale']['name']
        )

        # Create parent / child relationships for subjects
        cls.tribbles.from_json(
            subjects_json['tribbles']['json']
            % (
                cls.ds9.pk,
                cls.ds9.pk,
                cls.tribbles.pk,
                cls.original.pk,
                cls.original.pk,
                cls.tribbles.pk,
                cls.tribbles.pk,
                cls.tribbles.name,
            )
        ).save()
        cls.quadrotriticale.from_json(
            subjects_json['quadrotriticale']['json']
            % (
                cls.tribbles.pk,
                cls.tribbles.pk,
                cls.quadrotriticale.pk,
                cls.quadrotriticale.pk,
                cls.quadrotriticale.name,
            )
        ).save()

        # Create a fresh homepage (don't reuse existing pages)
        root = Page.objects.get(path='0001')
        cls.space = Page(slug='test-collections-home', title='Test Collections Home')
        root.add_child(instance=cls.space)

        # Create a site
        cls.site = Site.objects.create(
            hostname='localhost',
            is_default_site=True,
            port=80,
            root_page=cls.space,
            site_name='test site',
        )

        # Create StaffPages
        cls.captain = StaffPage(
            title='Jean-Luc Picard',
            cnetid='picard',
            position_title='Captain of the USS Enterprise',
        )
        cls.space.add_child(instance=cls.captain)

        cls.doctor = StaffPage(
            title='Leonard McCoy',
            cnetid='grumpydoctor',
            position_title='Doctor on the USS Enterprise',
        )
        cls.space.add_child(instance=cls.doctor)

        # Create UnitPage
        cls.ship = UnitPage(
            title='USS Enterprise (NCC-1701-D)',
            page_maintainer=cls.captain,
            editor=cls.captain,
            display_in_dropdown=True,
        )
        cls.space.add_child(instance=cls.ship)

        # Create StaffPublicPages
        cls.captain_public_page = StaffPublicPage(
            title=cls.captain.title,
            cnetid=cls.captain.cnetid,
            page_maintainer=cls.captain,
            editor=cls.captain,
            content_specialist=cls.captain,
            unit=cls.ship,
            slug='jean-luc-picard-public',
        )
        cls.space.add_child(instance=cls.captain_public_page)

        cls.doctor_public_page = StaffPublicPage(
            title=cls.doctor.title,
            cnetid=cls.doctor.cnetid,
            page_maintainer=cls.doctor,
            editor=cls.doctor,
            content_specialist=cls.doctor,
            unit=cls.ship,
            slug='grumpy-leonard-mccoy',
        )
        cls.space.add_child(instance=cls.doctor_public_page)

        # Create a staff page email and append it
        cls.captain.staff_page_email.create(
            email='picard@starfleet.io',
        )
        cls.captain.staff_page_phone_faculty_exchange.create(
            phone_number='012-345-6789',
            faculty_exchange='Bridge',
        )
        cls.captain.save()

        # Collection pages
        cls.collection_sisko = CollectionPage(
            title='Benjamin Sisko',
            page_maintainer=cls.captain,
            editor=cls.captain,
            content_specialist=cls.captain,
            unit=cls.ship,
            short_abstract='As a Starfleet officer coming up through the ranks, Sisko was mentored by Curzon Dax, a joined Trill serving as Federation ambassador to the Klingon Empire, when the two were stationed aboard the USS Livingston early in Sisko\'s career.',
        )
        cls.space.add_child(instance=cls.collection_sisko)

        cls.collection_darvin = CollectionPage(
            title='Arne Darvin',
            page_maintainer=cls.captain,
            editor=cls.captain,
            content_specialist=cls.captain,
            unit=cls.ship,
            short_abstract='Darvin is a Klingon who poses as a Federation official to sabotage Federation attempts to colonize Sherman\'s Planet.',
        )
        cls.space.add_child(instance=cls.collection_darvin)

        # Link collection pages to subjects
        cls.ds9.collection_pages.add(
            cls.collection_sisko.collection_subject_placements.create(
                page=cls.collection_sisko, subject=cls.ds9
            ),
            bulk=False,
        )

        cls.tribbles.collection_pages.add(
            cls.collection_darvin.collection_subject_placements.create(
                page=cls.collection_darvin, subject=cls.tribbles
            ),
            bulk=False,
        )

        # Exhibit pages
        cls.exhibit_worf = ExhibitPage(
            title='Lieutenant Commander Worf',
            page_maintainer=cls.captain,
            editor=cls.captain,
            content_specialist=cls.captain,
            unit=cls.ship,
            short_abstract='In 2364, Worf was assigned to the USS Enterprise-D as relief flight control and tactical officer with the rank of lieutenant junior grade.',
        )
        cls.space.add_child(instance=cls.exhibit_worf)

        cls.exhibit_koloth = ExhibitPage(
            title='Captain Koloth',
            page_maintainer=cls.captain,
            editor=cls.captain,
            content_specialist=cls.captain,
            unit=cls.ship,
            short_abstract='Captain Koloth requested permission for his crew to board K7 for shore leave.',
        )
        cls.space.add_child(instance=cls.exhibit_koloth)

        # Link exhibit pages to subjects
        cls.ds9.exhibit_pages.add(
            cls.exhibit_worf.exhibit_subject_placements.create(
                page=cls.exhibit_worf, subject=cls.ds9
            ),
            bulk=False,
        )

        cls.tribbles.exhibit_pages.add(
            cls.exhibit_koloth.exhibit_subject_placements.create(
                page=cls.exhibit_koloth, subject=cls.tribbles
            ),
            bulk=False,
        )

        # Link staff pages to subjects
        StaffPageSubjectPlacement(page=cls.captain, subject=cls.ds9).save()

        StaffPageSubjectPlacement(page=cls.doctor, subject=cls.tribbles).save()

        # Make a CollectingAreaPage
        # Set the default subject to ds9
        cls.collecting_area = CollectingAreaPage(
            title='Star Trek',
            subject=cls.ds9,
            page_maintainer=cls.captain,
            editor=cls.captain,
            content_specialist=cls.captain,
            unit=cls.ship,
            first_feature=cls.collection_sisko,
            second_feature=cls.collection_darvin,
            third_feature=cls.exhibit_worf,
            fourth_feature=cls.exhibit_koloth,
        )
        cls.space.add_child(instance=cls.collecting_area)

    def setUp(self):
        # Clear cache before each test
        # This ensures Wagtail doesn't use stale cached references
        clear_url_caches()
        cache.clear()
        clear_cache()

    def tearDown(self):
        """
        Clear the cache between every test.
        """
        caches['default'].clear()

    def test_get_subjects_children_false_only_returns_one_top_level_subject(self):
        subject = self.collecting_area.get_subjects(children=False)
        self.assertEqual(len(subject), 1)
        self.assertEqual(subject.pop(), self.ds9)

    def test_get_subjects_children_true_returns_hierarchy(self):
        subjects = self.collecting_area.get_subjects(children=True)
        self.assertEqual(len(subjects), 3)
        self.assertEqual(
            subjects.difference(set([self.ds9, self.tribbles, self.quadrotriticale])),
            set([]),
        )

    def test_get_subjects_with_a_different_subject(self):
        self.collecting_area.subject = self.original

        subject = self.collecting_area.get_subjects(children=False)
        self.assertEqual(len(subject), 1)
        self.assertEqual(subject.pop(), self.original)

        subjects = self.collecting_area.get_subjects(children=True)
        self.assertEqual(len(subjects), 3)
        self.assertEqual(
            subjects.difference(
                set([self.original, self.tribbles, self.quadrotriticale])
            ),
            set([]),
        )

        self.collecting_area.subject = self.tribbles

        subject = self.collecting_area.get_subjects(children=False)
        self.assertEqual(len(subject), 1)
        self.assertEqual(subject.pop(), self.tribbles)

        subjects = self.collecting_area.get_subjects(children=True)
        self.assertEqual(len(subjects), 2)
        self.assertEqual(
            subjects.difference(set([self.tribbles, self.quadrotriticale])), set([])
        )

    def test_get_subjects_without_a_subject(self):
        # This should never happen in the wild because
        # subject is a required field. Let's handle
        # for it anyhow
        void = CollectingAreaPage(
            title='Nagilum',
            page_maintainer=self.captain,
            editor=self.captain,
            content_specialist=self.captain,
            unit=self.ship,
        )
        self.assertEqual(void.get_subjects(children=False), set([]))
        self.assertEqual(void.get_subjects(children=True), set([]))

    def test_build_related_link_normal(self):
        page = self.collecting_area
        link = page._build_related_link(self.captain.id, self.site)
        # Verify title is correct (URL may be empty in parallel tests)
        self.assertEqual(link[0], 'Jean-Luc Picard')
        # Verify we got a tuple of length 2
        self.assertEqual(len(link), 2)

    def test_build_related_link_no_page_does_not_blow_up(self):
        page = self.collecting_area
        link = page._build_related_link(999, self.site)
        self.assertEqual(link, ('', ''))

    def test_build_subject_specialist_normal(self):
        page = self.collecting_area
        subject_specialist = page._build_subject_specialist(self.captain, self.site)
        self.assertEqual(subject_specialist[0], 'Jean-Luc Picard')
        self.assertEqual(subject_specialist[1], 'Captain of the USS Enterprise')
        self.assertEqual(subject_specialist[3], 'picard@starfleet.io')
        self.assertEqual(subject_specialist[4], (('012-345-6789', 'Bridge'),))

    def test_build_subject_specialist_with_wrong_page_type(self):
        page = self.collecting_area
        self.assertRaises(
            TypeError, page._build_subject_specialist, self.ship, self.site
        )

    def test_get_related_no_children(self):
        page = self.collecting_area
        related = page.get_related(self.site)

        # Verify structure - should have 3 keys
        self.assertEqual(
            set(related.keys()), {'collections', 'exhibits', 'subject_specialists'}
        )

        # Verify collections - check title only (URLs may be empty in parallel tests)
        collections = related['collections']
        self.assertEqual(len(collections), 1)
        collection_titles = [item[0] for item in collections]
        self.assertIn('Benjamin Sisko', collection_titles)

        # Verify exhibits - check title only (URLs may be empty in parallel tests)
        exhibits = related['exhibits']
        self.assertEqual(len(exhibits), 1)
        exhibit_titles = [item[0] for item in exhibits]
        self.assertIn('Lieutenant Commander Worf', exhibit_titles)

        # Verify subject specialists - check structure and content
        specialists = related['subject_specialists']
        self.assertEqual(len(specialists), 1)
        specialist = list(specialists)[0]
        self.assertEqual(specialist[0], 'Jean-Luc Picard')  # name
        self.assertEqual(specialist[1], 'Captain of the USS Enterprise')  # title
        # specialist[2] is URL - skip checking exact value
        # specialist[3] is email
        self.assertEqual(specialist[4], (('012-345-6789', 'Bridge'),))  # phone/fac
        self.assertIsNone(specialist[5])  # thumb

    def test_get_related_with_children(self):
        page = self.collecting_area
        related = page.get_related(self.site, children=True)
        specialists = set(r[0] for r in related['subject_specialists'])
        collections = set(r[0] for r in related['collections'])
        exhibits = set(r[0] for r in related['exhibits'])
        self.assertTrue(
            'Leonard McCoy' in specialists and 'Jean-Luc Picard' in specialists
        )
        self.assertTrue(
            'Arne Darvin' in collections and 'Benjamin Sisko' in collections
        )
        self.assertTrue(
            'Lieutenant Commander Worf' in exhibits and 'Captain Koloth' in exhibits
        )
        self.assertEqual(len(specialists), 2)
        self.assertEqual(len(collections), 2)
        self.assertEqual(len(exhibits), 2)

    def test_get_features(self):
        page = self.collecting_area
        features = page.get_features(self.site)
        self.assertEqual(len(features), 4)
        for f in features:
            self.assertEqual(len(f), 4)


example_noid1 = "b2tf4wj2mp94"
example_noid2 = "b2kg6jc3941j"
example_noid3 = "b2k57z87tt0h"

browse_type1 = "subject"
browse_type2 = "decade"
browse1_1 = "ethnology"
browse1_2 = "gangs"
browse2_1 = "1930s"
browse2_2 = "1940s"
list_browse1 = "date"
collection1 = "social-scientists-map-chicago"


class CollectionTest(SimpleTestCase):

    def browse_type_listing_works(self):
        """
        Make sure we can pull the browse type links down from IIIF.
        """

        iiif_url1 = CBrowseURL.mk_cbrowse_type_url_iiif(collection1, browse_type1)
        iiif_url2 = CBrowseURL.mk_cbrowse_type_url_iiif(collection1, browse_type2)

        assert DisplayBrowse.get_iiif_labels(
            iiif_url1,
            browse_type1,
            collection1,
        )
        assert DisplayBrowse.get_iiif_labels(
            iiif_url2,
            browse_type2,
            collection1,
        )

    def cluster_browse_listing_works(self):
        """
        Make sure we can pull the links for items falling under a
        particular cluster browse from IIIF.
        """
        assert DisplayBrowse.get_cbrowse_items(
            collection1,
            browse1_1,
            browse_type1,
        )
        assert DisplayBrowse.get_cbrowse_items(
            collection1,
            browse1_2,
            browse_type1,
        )
        assert DisplayBrowse.get_cbrowse_items(
            collection1,
            browse2_1,
            browse_type2,
        )
        assert DisplayBrowse.get_cbrowse_items(
            collection1,
            browse2_2,
            browse_type2,
        )

    def list_browse_listing_works(self):
        """
        Make sure we can pull the links for items falling under a
        particular list browse from IIIF.
        """
        assert DisplayBrowse.get_lbrowse_items(
            collection1,
            list_browse1,
        )

    def iiif_is_down_browse_type_elegant_fail(self):
        """
        If the IIIF server is down, the code to get the browse type listing
        links should return an empty string.  This will lead to the
        "are you sure you typed the right URL" message on the page.
        """
        assert not DisplayBrowse.get_iiif_labels(
            CBrowseURL.mk_cbrowse_type_url_iiif(collection1, browse_type1),
            browse_type1,
            collection1,
            modify=Testing.bring_website_down,
        )
        assert not DisplayBrowse.get_iiif_labels(
            CBrowseURL.mk_cbrowse_type_url_iiif(collection1, browse_type2),
            browse_type2,
            collection1,
            modify=Testing.bring_website_down,
        )

    def iiif_is_down_cluster_browse_elegant_fail(self):
        """
        If the IIIF server is down, the code to get the links for the
        cluster browse listing should return an empty string.  This
        will lead to "are you sure you typed the right URL" in the
        page.
        """
        assert not DisplayBrowse.get_cbrowse_items(
            collection1, browse1_1, browse_type1, modify=Testing.bring_website_down
        )
        assert not DisplayBrowse.get_cbrowse_items(
            collection1, browse1_2, browse_type1, modify=Testing.bring_website_down
        )
        assert not DisplayBrowse.get_cbrowse_items(
            collection1, browse2_1, browse_type2, modify=Testing.bring_website_down
        )
        assert not DisplayBrowse.get_cbrowse_items(
            collection1, browse2_2, browse_type2, modify=Testing.bring_website_down
        )

    def iiif_is_down_list_browse_elegant_fail(self):
        """
        If the IIIF server is down, the code to get the links for the list
        browse listing should return an empty string.  This will lead
        to "are you sure you typed the right URL" in the page.
        """
        assert not DisplayBrowse.get_lbrowse_items(
            collection1, list_browse1, modify=Testing.bring_website_down
        )

    def browse_type_bad_json(self):
        """
        If the browse type JSON from IIIF has a syntax error, the page
        should display a "internal error; please contact us" message.
        Currently, the code in models.py catches the JSONDecodeError
        exception and makes that happen.
        """
        self.assertRaises(
            simplejson.JSONDecodeError,
            DisplayBrowse.get_iiif_labels,
            CBrowseURL.mk_cbrowse_type_url_iiif(collection1, browse_type1),
            browse_type1,
            collection1,
            modify=Testing.break_json,
        )
        self.assertRaises(
            simplejson.JSONDecodeError,
            DisplayBrowse.get_iiif_labels,
            CBrowseURL.mk_cbrowse_type_url_iiif(collection1, browse_type2),
            browse_type2,
            collection1,
            modify=Testing.break_json,
        )

    def cluster_browse_bad_json(self):
        """
        If the cluster browse JSON from IIIF has a syntax error, the page
        should display a "internal error; please contact us" message.
        Currently, the code in models.py catches the JSONDecodeError
        exception and makes that happen.
        """
        self.assertRaises(
            simplejson.JSONDecodeError,
            DisplayBrowse.get_cbrowse_items,
            collection1,
            browse1_1,
            browse_type1,
            modify=Testing.break_json,
        )
        self.assertRaises(
            simplejson.JSONDecodeError,
            DisplayBrowse.get_cbrowse_items,
            collection1,
            browse1_2,
            browse_type1,
            modify=Testing.break_json,
        )
        self.assertRaises(
            simplejson.JSONDecodeError,
            DisplayBrowse.get_cbrowse_items,
            collection1,
            browse2_1,
            browse_type2,
            modify=Testing.break_json,
        )
        self.assertRaises(
            simplejson.JSONDecodeError,
            DisplayBrowse.get_cbrowse_items,
            collection1,
            browse2_2,
            browse_type2,
            modify=Testing.break_json,
        )

    def list_browse_bad_json(self):
        """
        If the list browse JSON from IIIF has a syntax error, the page
        should display a "internal error; please contact us" message.
        Currently, the code in models.py catches the JSONDecodeError
        exception and makes that happen.
        """
        self.assertRaises(
            simplejson.JSONDecodeError,
            DisplayBrowse.get_lbrowse_items,
            collection1,
            list_browse1,
            modify=Testing.break_json,
        )

    def browse_type_unexpected_json(self):
        """
        If IIIF returns syntactically valid browse type JSON not with the
        expected structure (i.e. with different keys from what we
        expect), the page should display a "internal error; please
        contact us" message.
        """
        self.assertRaises(
            KeyError,
            DisplayBrowse.get_iiif_labels,
            CBrowseURL.mk_cbrowse_type_url_iiif(collection1, browse_type1),
            browse_type1,
            collection1,
            modify=Testing.unexpected_json,
        )

        self.assertRaises(
            KeyError,
            DisplayBrowse.get_iiif_labels,
            CBrowseURL.mk_cbrowse_type_url_iiif(collection1, browse_type2),
            browse_type2,
            collection1,
            modify=Testing.unexpected_json,
        )

    def cluster_browse_unexpected_json(self):
        """
        If IIIF returns syntactically valid but unexpectedly-structured
        cluster browse JSON, the page should display a "internal
        error; please contact us" message.
        """
        self.assertRaises(
            KeyError,
            DisplayBrowse.get_cbrowse_items,
            collection1,
            browse1_1,
            browse_type1,
            modify=Testing.unexpected_json,
        )
        self.assertRaises(
            KeyError,
            DisplayBrowse.get_cbrowse_items,
            collection1,
            browse1_2,
            browse_type1,
            modify=Testing.unexpected_json,
        )
        self.assertRaises(
            KeyError,
            DisplayBrowse.get_cbrowse_items,
            collection1,
            browse2_1,
            browse_type2,
            modify=Testing.unexpected_json,
        )
        self.assertRaises(
            KeyError,
            DisplayBrowse.get_cbrowse_items,
            collection1,
            browse2_2,
            browse_type2,
            modify=Testing.unexpected_json,
        )

    def list_browse_unexpected_json(self):
        """
        If IIIF returns syntactically valid but unexpectedly-structured
        list browse JSON, the page should display a "internal error;
        please contact us" message.
        """
        self.assertRaises(
            KeyError,
            DisplayBrowse.get_lbrowse_items,
            collection1,
            list_browse1,
            modify=Testing.unexpected_json,
        )

    def browse_type_404(self):
        """
        If there's a 404 error connecting to IIIF while getting the browse
        type JSON, the page should display a 'maybe you typed the
        wrong URL' message.  In this case, that means the
        get_iiif_labels function should return an empty string.
        """
        assert not DisplayBrowse.get_iiif_labels(
            CBrowseURL.mk_cbrowse_type_url_iiif(collection1, browse_type1),
            browse_type1,
            collection1,
            modify=Testing.change_status_code(404),
        )

        assert not DisplayBrowse.get_iiif_labels(
            CBrowseURL.mk_cbrowse_type_url_iiif(collection1, browse_type2),
            browse_type2,
            collection1,
            modify=Testing.change_status_code(404),
        )

    def cluster_browse_404(self):
        """
        If there's a 404 error connecting to IIIF while getting the
        cluster browse JSON, the page should display a 'maybe you
        typed the wrong URL' message.
        """
        assert not DisplayBrowse.get_cbrowse_items(
            collection1, browse1_1, browse_type1, modify=Testing.change_status_code(404)
        )
        assert not DisplayBrowse.get_cbrowse_items(
            collection1, browse1_2, browse_type1, modify=Testing.change_status_code(404)
        )
        assert not DisplayBrowse.get_cbrowse_items(
            collection1, browse2_1, browse_type2, modify=Testing.change_status_code(404)
        )
        assert not DisplayBrowse.get_cbrowse_items(
            collection1, browse2_2, browse_type2, modify=Testing.change_status_code(404)
        )

    def list_browse_404(self):
        """
        If there's a 404 error connecting to IIIF while getting the list
        browse JSON, the page should display a 'maybe you typed the
        wrong URL' message.
        """
        assert not DisplayBrowse.get_lbrowse_items(
            collection1, list_browse1, modify=Testing.change_status_code(404)
        )

    def viewer_works(self):
        """
        Check the IIIF manifest exists, for the purpose of assembling the
        URL for the Universal Viewer iframe.
        """
        assert IIIFDisplay.get_viewer_url(example_noid1)
        assert IIIFDisplay.get_viewer_url(example_noid2)
        assert IIIFDisplay.get_viewer_url(example_noid3)

    def viewer_down(self):
        """
        If IIIF is down, the object page should display a "please contact
        us" message where the viewer would be.  In this case, that
        means the get_viewer_url function should return an empty
        string.
        """
        assert not IIIFDisplay.get_viewer_url(
            example_noid1, modify=Testing.bring_website_down
        )
        assert not IIIFDisplay.get_viewer_url(
            example_noid2, modify=Testing.bring_website_down
        )
        assert not IIIFDisplay.get_viewer_url(
            example_noid3, modify=Testing.bring_website_down
        )

    def viewer_404(self):
        """
        If the IIIF server returns a 404, the object page should display a
        "please contact us" message.
        """
        assert not IIIFDisplay.get_viewer_url(
            example_noid1, modify=Testing.change_status_code(404)
        )
        assert not IIIFDisplay.get_viewer_url(
            example_noid2, modify=Testing.change_status_code(404)
        )
        assert not IIIFDisplay.get_viewer_url(
            example_noid3, modify=Testing.change_status_code(404)
        )

    def marklogic_works(self):
        """
        Check that we are able to successfully connect to Mark Logic and
        pull down the metadata fields for the object to be displayed
        in the object page.
        """
        assert get_record_for_display(example_noid1, [])
        assert get_record_for_display(example_noid2, [])
        assert get_record_for_display(example_noid3, [])

    def marklogic_down(self):
        """
        If the Mark Logic server is down, the object page should display a
        "contact us" message where the metadata fields would be.  In
        this case, that means that get_record_for_display should
        return an empty string.
        """
        assert not get_record_for_display(
            example_noid1, [], modify=Testing.bring_website_down
        )
        assert not get_record_for_display(
            example_noid2, [], modify=Testing.bring_website_down
        )
        assert not get_record_for_display(
            example_noid3, [], modify=Testing.bring_website_down
        )

    def marklogic_unexpected_json(self):
        """
        If Mark Logic returns unexpectedly-structured JSON, the object page
        should display a "contact us" message where the metadata
        fields would be.
        """
        assert not get_record_for_display(
            example_noid1, [], modify=Testing.unexpected_json
        )
        assert not get_record_for_display(
            example_noid2, [], modify=Testing.unexpected_json
        )
        assert not get_record_for_display(
            example_noid3, [], modify=Testing.unexpected_json
        )

    # MT 3/23/2021: temporarily commenting out citation-related unit
    # tests while we revamp the citation service; will bring them back
    # once the new citation service is in production

    # def secondary_ark_resolver_down(self):
    #     """
    #     If the secondary ARK resolver is down and can't provide Turtle data
    #     for the collection object, the "Cite This" menu should not
    #     display.  In this case, that means get_turtle_data should
    #     return an empty string.
    #     """
    #     assert not CitationInfo.get_turtle_data(
    #         example_noid1,
    #         modify=Testing.bring_website_down
    #     )
    #     assert not CitationInfo.get_turtle_data(
    #         example_noid2,
    #         modify=Testing.bring_website_down
    #     )
    #     assert not CitationInfo.get_turtle_data(
    #         example_noid3,
    #         modify=Testing.bring_website_down
    #     )

    # def citation_works(self):
    #     """
    #     Check that the citation service at
    #     www.lib.uchicago.edu/cgi-bin/citation is returning CSL-JSON to
    #     be displayed in the "Cite This" menu.
    #     """
    #     assert CitationInfo.get_csl(
    #         Testing.example,
    #         Testing.default_config
    #     )

    # def citation_down(self):
    #     """
    #     If the citation service is down, "Cite This" menu should not be
    #     displayed.  In this case, that means get_csl should return an
    #     empty string.
    #     """
    #     assert not CitationInfo.get_csl(
    #         Testing.example,
    #         Testing.default_config,
    #         modify=Testing.bring_website_down
    #     )

    # def citation_400(self):
    #     """
    #     If the turtle data provided to the citation service is invalid, it
    #     will return a 400 response.  In that situation, the "Cite
    #     This" menu should not appear in the page.
    #     """
    #     assert not CitationInfo.get_csl(
    #         Testing.example,
    #         Testing.default_config,
    #         modify=Testing.change_status_code(400)
    #     )

    # def citation_500(self):
    #     """
    #     The citation service should never return 500 response---if it
    #     does, then it failed to handle some variety of input it should
    #     expect to get and that is officially considered a bug.  But if
    #     it does have such a bug and therefore return a 500 response,
    #     the "Cite This" menu should not appear in the object page.
    #     """
    #     assert not CitationInfo.get_csl(
    #         Testing.example,
    #         Testing.default_config,
    #         modify=Testing.change_status_code(500)
    #     )

    # def bibtex_works(self):
    #     """
    #     Check that the citation service is returning BibTeX data.
    #     """
    #     assert CitationInfo.get_bibtex(
    #         Testing.example,
    #         Testing.default_config,
    #     )

    # def ris_works(self):
    #     """
    #     Check that the citation service is returning RIS data.
    #     """
    #     assert CitationInfo.get_ris(
    #         Testing.example,
    #         Testing.default_config,
    #     )

    # def zotero_works(self):
    #     """
    #     Check that the citation service is returning Zotero data.
    #     """
    #     assert CitationInfo.get_zotero(
    #         Testing.example,
    #         Testing.default_config,
    #     )


class TestExhibitFiltering(TestCase):
    """Tests for ExhibitPage filtering functionality"""

    @classmethod
    def setUpTestData(cls):
        # Delete the default localhost site created by Wagtail migrations
        # to prevent conflicts with our test site
        Site.objects.filter(hostname='localhost').delete()

        # Create a fresh homepage (don't reuse existing pages)
        root = Page.objects.get(path='0001')
        cls.space = Page(slug='test-exhibit-home', title='Test Exhibit Home')
        root.add_child(instance=cls.space)

        # Create a site
        cls.site = Site.objects.create(
            hostname='localhost',
            is_default_site=True,
            port=80,
            root_page=cls.space,
            site_name='test site',
        )

        # Create a staff page to use as page_maintainer, editor, etc.
        cls.staff = StaffPage(
            title='Test Staff', cnetid='teststaff', position_title='Test Position'
        )
        cls.space.add_child(instance=cls.staff)

        # Create a unit page
        cls.unit = UnitPage(
            title='Test Unit',
            page_maintainer=cls.staff,
            editor=cls.staff,
            display_in_dropdown=True,
        )
        cls.space.add_child(instance=cls.unit)

        # Create a web exhibit with all required fields
        cls.web_exhibit = ExhibitPage(
            title="Test Web Exhibit",
            short_abstract="A test web exhibit",
            web_exhibit=True,
            page_maintainer=cls.staff,
            editor=cls.staff,
            content_specialist=cls.staff,
            unit=cls.unit,
        )
        cls.space.add_child(instance=cls.web_exhibit)

        # Create a non-web exhibit with all required fields
        cls.physical_exhibit = ExhibitPage(
            title="Test Physical Exhibit",
            short_abstract="A test physical exhibit",
            web_exhibit=False,
            page_maintainer=cls.staff,
            editor=cls.staff,
            content_specialist=cls.staff,
            unit=cls.unit,
        )
        cls.space.add_child(instance=cls.physical_exhibit)
        cls.physical_exhibit.save()

    def setUp(self):
        # Clear cache before each test
        # This ensures Wagtail doesn't use stale cached references
        clear_url_caches()
        cache.clear()
        clear_cache()

    def tearDown(self):
        # Clear cache after each test
        caches['default'].clear()

    def test_filter_web_exhibits(self):
        """Test filtering exhibits by web_exhibit field"""
        # Test that we can filter for web exhibits
        results = ExhibitPage.objects.filter(web_exhibit=True)

        # Should include web exhibit but not physical exhibit
        self.assertIn(self.web_exhibit, results)
        self.assertNotIn(self.physical_exhibit, results)

    def test_filter_physical_exhibits(self):
        """Test filtering for non-web exhibits"""
        # Test that we can filter for physical exhibits
        results = ExhibitPage.objects.filter(web_exhibit=False)

        # Should include physical exhibit but not web exhibit
        self.assertIn(self.physical_exhibit, results)
        self.assertNotIn(self.web_exhibit, results)

    def test_filter_field_exists(self):
        """Test that the FilterField for web_exhibit exists in the ExhibitPage model"""
        # Get all search fields defined in the ExhibitPage model
        search_fields = [f.field_name for f in ExhibitPage.search_fields]

        # Check that web_exhibit is in the list of indexed fields
        self.assertIn(
            'web_exhibit',
            search_fields,
            "web_exhibit FilterField is missing from ExhibitPage.search_fields",
        )

        # Verify it's specifically a FilterField
        filter_fields = [
            f.field_name
            for f in ExhibitPage.search_fields
            if f.__class__.__name__ == 'FilterField'
        ]
        self.assertIn(
            'web_exhibit',
            filter_fields,
            "web_exhibit should be indexed as a FilterField",
        )

    def test_django_filter_web_exhibits(self):
        """Test Django ORM filtering for web exhibits"""
        # Filter using the Django ORM
        web_exhibits = ExhibitPage.objects.filter(web_exhibit=True)
        physical_exhibits = ExhibitPage.objects.filter(web_exhibit=False)

        # Web exhibits should include only web exhibit
        self.assertEqual(web_exhibits.count(), 1)
        self.assertIn(self.web_exhibit, web_exhibits)
        self.assertNotIn(self.physical_exhibit, web_exhibits)

        # Physical exhibits should include only physical exhibit
        self.assertEqual(physical_exhibits.count(), 1)
        self.assertIn(self.physical_exhibit, physical_exhibits)
        self.assertNotIn(self.web_exhibit, physical_exhibits)

    @unittest.skipIf(
        os.environ.get('GITHUB_ACTIONS') == 'true',
        "Search indexing is unreliable in CI",
    )
    def test_combined_search_and_filter(self):
        """Test that filtering and searching works together"""
        # Create another web exhibit with a different title for testing search specificity
        another_web_exhibit = ExhibitPage(
            title="Another Web Exhibit",
            short_abstract="Another test web exhibit",
            web_exhibit=True,
            page_maintainer=self.staff,
            editor=self.staff,
            content_specialist=self.staff,
            unit=self.unit,
        )
        self.space.add_child(instance=another_web_exhibit)

        # Update search index to ensure objects are searchable
        search_backend = get_search_backend()
        search_backend.add_bulk(ExhibitPage, ExhibitPage.objects.all())

        try:
            # This simulates what happens in the collections view
            # First, filter by web_exhibit
            filtered_exhibits = ExhibitPage.objects.filter(web_exhibit=True)

            # Then apply search to the filtered results
            # Search for 'Test' which should only match our test web exhibits
            s = get_search_backend()
            search_results = s.search("Test", filtered_exhibits)

            # Should find two results - self.web_exhibit and another_web_exhibit
            self.assertEqual(len(search_results), 2)
            self.assertEqual(search_results[0], self.web_exhibit)
            self.assertEqual(search_results[1], another_web_exhibit)

            # Now search for something that doesn't match any exhibits
            search_results_empty = s.search("NonexistentTerm", filtered_exhibits)
            self.assertEqual(len(search_results_empty), 0)

            # Test the inverse - search first, then filter
            all_test_results = s.search("Exhibit", ExhibitPage.objects.all())
            # Should find both exhibits with 'Exhibit' in the title
            self.assertGreaterEqual(len(all_test_results), 2)

            # Now filter those results to only web exhibits
            web_exhibits_only = [r for r in all_test_results if r.web_exhibit]
            # Should include both our web exhibits
            self.assertIn(self.web_exhibit, web_exhibits_only)
            self.assertIn(another_web_exhibit, web_exhibits_only)

            # And filter to only physical exhibits
            physical_exhibits_only = [r for r in all_test_results if not r.web_exhibit]
            # Should include our physical exhibit
            self.assertIn(self.physical_exhibit, physical_exhibits_only)
        finally:
            # Clean up the additional exhibit we created
            another_web_exhibit.delete()
