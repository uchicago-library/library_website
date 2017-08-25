from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser
from lib_collections.views import collections
from lib_collections.models import CollectingAreaPage, CollectionPage, ExhibitPage
from django.core.cache import caches
from django.urls import reverse
from subjects.models import Subject
from units.models import UnitPage
from public.models import LocationPage, StaffPublicPage
from wagtail.wagtailcore.models import Page, Site
from staff.models import StaffPage, StaffPageEmailAddresses, StaffPageSubjectPlacement
from units.models import UnitPage

import time

class test_lib_collections_view(TestCase):
    fixtures = ['test.json']

    def setUp(self):
        self.factory = RequestFactory()
        self.user = AnonymousUser()
        self.startTime = time.time()
        # set up factory request

    def tearDown(self):
        t = time.time() - self.startTime
        #print("%s: %.3f" % (self.id(), t))

        caches['default'].clear()
        # clear cache

    def test_view(self):
        request = self.factory.get('/collection/')
        request.user = self.user
        response = collections(request)

        self.assertEqual(response.status_code, 200)

        t = time.time() - self.startTime
        #print("%s: %.3f" % (self.id(), t))

    def test_view_collections(self):
        request = self.factory.get('/collection/?view=collections')
        request.user = self.user
        response = collections(request)

        self.assertEqual(response.status_code, 200)

        t = time.time() - self.startTime
        #print("%s: %.3f" % (self.id(), t))

    def test_collections_digital(self):
        request = self.factory.get('/collection/?view=collections&digital=on')
        request.user = self.user
        response = collections(request)

#        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<input name="digital" type="checkbox" arial-label="limit to digital collections" id="checkboxdigital" checked="checked">', html=True)

        t = time.time() - self.startTime
        #print("%s: %.3f" % (self.id(), t))

    def test_collections_format(self):
        formats_list = ['Archives & Manuscripts', 'Audio', 'Books & Journals', \
'Images', 'Maps', 'Microform', 'Music Scores', 'Photographs', 'Reference Works', \
'Statistics & Datasets', 'Video']

        for f in formats_list:
            request = self.factory.get('/collection/?view=collections&format=%s' % f)

        t = time.time() - self.startTime
        #print("%s: %.3f" % (self.id(), t))

    def test_collections_location(self):
        locations_list = list(LocationPage.objects.live().values_list('title', flat=True))
        for l in locations_list:
            request = self.factory.get('/collection/?view=collections&location=%s' % l)
            request.user = self.user
            response = collections(request)

            self.assertEqual(response.status_code, 200)

    def test_collections_subject(self):
        subjects_list = list(Subject.objects.all().values_list("name", flat=True))
        for s in subjects_list:
            request = self.factory.get('/collection/?view=collections&subject=%s' % s)
            request.user = self.user
            response = collections(request)

            self.assertEqual(response.status_code, 200)

        t = time.time() - self.startTime
        #print("%s: %.3f" % (self.id(), t))

    #def test_collections_unit(self):
    #    unit_list = list(UnitPage.objects.all().values_list("title", flat=True))
    #    for u in unit_list:
    #        request = self.factory.get('/collection/?view=collections&unit=%s' % u)
    #        request.user = self.user
    #        response = collections(request)
    #        self.assertEqual(response.status_code, 200)
    #    t = time.time() - self.startTime
    #    print("%s: %.3f" % (self.id(), t))

    def test_view_exhibit(self):
        request = self.factory.get('/collection/?view=exhibits')
        request.user = self.user
        response = collections(request)

        self.assertEqual(response.status_code, 200)

        t = time.time() - self.startTime
        #print("%s: %.3f" % (self.id(), t))

    def test_exhibit_location_none(self):
        request = self.factory.get('/collection/?view=exhibits&location=%s' % None)
        request.user = self.user
        response = collections(request)

        self.assertEqual(response.status_code, 200)

        t = time.time() - self.startTime
        #print("%s: %.3f" % (self.id(), t))

    def test_exhibit_subject_none(self):
        request = self.factory.get('/collection/?view=exhibits&subject=%s' % None)
        request.user = self.user
        response = collections(request)

        self.assertEqual(response.status_code, 200)

        t = time.time() - self.startTime
        #print("%s: %.3f" % (self.id(), t))

    #def test_exhibit_unit_none(self):
    #    request = self.factory.get('/collection/?view=exhibits&unit=%s' % None)
    #    request.user = self.user
    #    response = collections(request)
    #    self.assertEqual(response.status_code, 200)
    #    t = time.time() - self.startTime
    #    print("%s: %.3f" % (self.id(), t))

    def test_exhibit_digital_none(self):
        request = self.factory.get('/collection/?view=exhibits&digital=%s' % None)
        request.user = self.user
        response = collections(request)

        self.assertEqual(response.status_code, 200)

        t = time.time() - self.startTime
        #print("%s: %.3f" % (self.id(), t))

    def test_view_subjects(self):
        request = self.factory.get('/collection/?view=subjects')
        request.user = self.user
        response = collections(request)

        self.assertEqual(response.status_code, 200)

        t = time.time() - self.startTime
        #print("%s: %.3f" % (self.id(), t))

    def test_view_none(self):
        request = self.factory.get('/collection/?view=%s' % None)
        request.user = self.user
        response = collections(request)

        self.assertEqual(response.status_code, 200)

        t = time.time() - self.startTime
        #print("%s: %.3f" % (self.id(), t))

    def test_view_invalid(self):
        request = self.factory.get('/collection/?view=gibberish')
        request.user = self.user
        response = collections(request)

        self.assertEqual(response.status_code, 200)

        t = time.time() - self.startTime
        #print("%s: %.3f" % (self.id(), t))

    #def test_sorted(self):
    #    request = self.factory.get('/collection/')
    #    request.user = self.user
    #    response = collections(request)
    #    self.assertEqual(response['collections'].is_sorted, True)
    #    self.assertEqual(response['subjects'].is_sorted, True)


class TestCollectingAreaPages(TestCase):

    def setUp(self):

        # Configuration for subjects
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
            }
        }

        # Create subjects to operate on
        Subject.objects.create(name=subjects_json['tng']['name']).save()
        Subject.objects.create(name=subjects_json['ds9']['name']).save()
        Subject.objects.create(name=subjects_json['original']['name']).save()
        Subject.objects.create(name=subjects_json['tribbles']['name']).save()
        Subject.objects.create(name=subjects_json['quadrotriticale']['name']).save()

        # Load the subjects into variables
        subjects = Subject.objects.all()
        self.tng = subjects.get(name=subjects_json['tng']['name'])
        self.ds9 = subjects.get(name=subjects_json['ds9']['name'])
        self.original = subjects.get(name=subjects_json['original']['name'])
        self.tribbles = subjects.get(name=subjects_json['tribbles']['name'])
        self.quadrotriticale = subjects.get(name=subjects_json['quadrotriticale']['name'])

        # Create parent / child relationships for subjects
        self.tribbles.from_json(subjects_json['tribbles']['json'] % (self.ds9.pk, self.ds9.pk, self.tribbles.pk, self.original.pk, self.original.pk, self.tribbles.pk, self.tribbles.pk, self.tribbles.name)).save()
        self.quadrotriticale.from_json(subjects_json['quadrotriticale']['json'] % (self.tribbles.pk, self.tribbles.pk, self.quadrotriticale.pk, self.quadrotriticale.pk, self.quadrotriticale.name)).save()

        # Get the default homepage
        self.space = Page.objects.get(id=2) # Homepage

        # Create a site 
        self.site = Site.objects.create(root_page=self.space)

        # Create StaffPages
        self.captain = StaffPage(
            title='Jean-Luc Picard',
            cnetid='picard',
            position_title='Captain of the USS Enterprise'
        )
        self.space.add_child(instance=self.captain)

        self.doctor = StaffPage(
            title='Leonard McCoy',
            cnetid='grumpydoctor',
            position_title='Doctor on the USS Enterprise'
        )
        self.space.add_child(instance=self.doctor)

        # Create UnitPage
        self.ship = UnitPage(
            title='USS Enterprise (NCC-1701-D)',
            page_maintainer=self.captain,
            editor=self.captain,
            display_in_dropdown=True
        )
        self.space.add_child(instance=self.ship)

        # Create StaffPublicPages
        self.captain_public_page = StaffPublicPage(
            title=self.captain.title,
            cnetid=self.captain.cnetid,
            page_maintainer=self.captain,
            editor=self.captain,
            content_specialist=self.captain,
            unit=self.ship,
            slug='jean-luc-picard-public',
        )
        self.space.add_child(instance=self.captain_public_page)

        self.doctor_public_page = StaffPublicPage(
            title=self.doctor.title,
            cnetid=self.doctor.cnetid,
            page_maintainer=self.doctor,
            editor=self.doctor,
            content_specialist=self.doctor,
            unit=self.ship,
            slug='grumpy-leonard-mccoy',
        )
        self.space.add_child(instance=self.doctor_public_page)

        # Create a staff page email and append it
        self.captain.staff_page_email.create(
            sort_order='None',
            id=self.captain.id,
            page_id=4,
            page = self.captain,
            email='picard@starfleet.io'
        )
        self.captain.staff_page_phone_faculty_exchange.create(
            sort_order='None',
            id=self.captain.id,
            page_id=4,
            page = self.captain,
            phone_number='012-345-6789',
            faculty_exchange = 'Bridge'
        )

        # Collection pages
        self.collection_sisko = CollectionPage(
            title='Benjamin Sisko',
            page_maintainer=self.captain,
            editor=self.captain,
            content_specialist=self.captain,
            unit=self.ship,
            short_abstract='As a Starfleet officer coming up through the ranks, Sisko was mentored by Curzon Dax, a joined Trill serving as Federation ambassador to the Klingon Empire, when the two were stationed aboard the USS Livingston early in Sisko\'s career.'
        )
        self.space.add_child(instance=self.collection_sisko)

        self.collection_darvin = CollectionPage(
            title='Arne Darvin',
            page_maintainer=self.captain,
            editor=self.captain,
            content_specialist=self.captain,
            unit=self.ship,
            short_abstract='Darvin is a Klingon who poses as a Federation official to sabotage Federation attempts to colonize Sherman\'s Planet.'
        )
        self.space.add_child(instance=self.collection_darvin)

        # Link collection pages to subjects
        self.ds9.collection_pages.add(
            self.collection_sisko.collection_subject_placements.create(
                page=self.collection_sisko,
                subject=self.ds9
            ),
            bulk=False
        )

        self.tribbles.collection_pages.add(
            self.collection_darvin.collection_subject_placements.create(
                page=self.collection_darvin,
                subject=self.tribbles
            ),
            bulk=False
        )

        # Exhibit pages
        self.exhibit_worf = ExhibitPage(
            title='Lieutenant Commander Worf',
            page_maintainer=self.captain,
            editor=self.captain,
            content_specialist=self.captain,
            unit=self.ship,
            short_abstract='In 2364, Worf was assigned to the USS Enterprise-D as relief flight control and tactical officer with the rank of lieutenant junior grade.'
        )
        self.space.add_child(instance=self.exhibit_worf)

        self.exhibit_koloth = ExhibitPage(
            title='Captain Koloth',
            page_maintainer=self.captain,
            editor=self.captain,
            content_specialist=self.captain,
            unit=self.ship,
            short_abstract='Captain Koloth requested permission for his crew to board K7 for shore leave.'
        )
        self.space.add_child(instance=self.exhibit_koloth)

        # Link exhibit pages to subjects
        self.ds9.exhibit_pages.add(
            self.exhibit_worf.exhibit_subject_placements.create(
                page=self.exhibit_worf,
                subject=self.ds9
            ),
            bulk=False
        )

        self.tribbles.exhibit_pages.add(
            self.exhibit_koloth.exhibit_subject_placements.create(
                page=self.exhibit_koloth,
                subject=self.tribbles
            ),
            bulk=False
        )

        # Link staff pages to subjects
        StaffPageSubjectPlacement(
            page = self.captain,
            subject = self.ds9
        ).save()

        StaffPageSubjectPlacement(
            page = self.doctor,
            subject = self.tribbles
        ).save()

        # Make a CollectingAreaPage
        # Set the default subject to tng
        self.collecting_area = CollectingAreaPage(
            title='Star Trek',
            subject=self.ds9,
            page_maintainer=self.captain,
            editor=self.captain,
            content_specialist=self.captain,
            unit=self.ship,
            first_feature = self.collection_sisko,
            second_feature = self.collection_darvin,
            third_feature = self.exhibit_worf,
            fourth_feature = self.exhibit_koloth
        )
        self.space.add_child(instance=self.collecting_area)


    def test_get_subjects_children_false_only_returns_one_top_level_subject(self):
        subject = self.collecting_area.get_subjects(children=False)
        self.assertEqual(len(subject), 1)
        self.assertEqual(subject.pop(), self.ds9)

    def test_get_subjects_children_true_returns_hierarchy(self):
        subjects = self.collecting_area.get_subjects(children=True)
        self.assertEqual(len(subjects), 3)
        self.assertEqual(subjects.difference(set([self.ds9, self.tribbles, self.quadrotriticale])), set([]))

    def test_get_subjects_with_a_different_subject(self):
        self.collecting_area.subject = self.original

        subject = self.collecting_area.get_subjects(children=False)
        self.assertEqual(len(subject), 1)
        self.assertEqual(subject.pop(), self.original)

        subjects = self.collecting_area.get_subjects(children=True)
        self.assertEqual(len(subjects), 3)
        self.assertEqual(subjects.difference(set([self.original, self.tribbles, self.quadrotriticale])), set([]))

        self.collecting_area.subject = self.tribbles

        subject = self.collecting_area.get_subjects(children=False)
        self.assertEqual(len(subject), 1)
        self.assertEqual(subject.pop(), self.tribbles)

        subjects = self.collecting_area.get_subjects(children=True)
        self.assertEqual(len(subjects), 2)
        self.assertEqual(subjects.difference(set([self.tribbles, self.quadrotriticale])), set([]))

    def test_get_subjects_without_a_subject(self):
        # This should never happen in the wild because
        # subject is a required field. Let's handle
        # for it anyhow
        void = CollectingAreaPage(title='Nagilum', page_maintainer=self.captain, editor=self.captain, content_specialist=self.captain, unit=self.ship)
        self.assertEqual(void.get_subjects(children=False), set([]))
        self.assertEqual(void.get_subjects(children=True), set([]))

    def test_build_related_link_normal(self):
        page = self.collecting_area
        link = page._build_related_link(self.captain.id)
        self.assertEqual(link, ('Jean-Luc Picard', '/jean-luc-picard/'))

    def test_build_related_link_no_page_does_not_blow_up(self):
        page = self.collecting_area
        link = page._build_related_link(999)
        self.assertEqual(link, ('', ''))

    def test_build_subject_specialist_normal(self):
        page = self.collecting_area
        subject_specialist = page._build_subject_specialist(self.captain)
        self.assertEqual(subject_specialist, ('Jean-Luc Picard', 'Captain of the USS Enterprise', '/jean-luc-picard-public/', 'picard@starfleet.io', (('012-345-6789', 'Bridge'),), None))

    def test_build_subject_specialist_with_wrong_page_type(self):
        page = self.collecting_area
        self.assertRaises(TypeError, page._build_subject_specialist, self.ship)

    def test_get_related_no_children(self):
        page = self.collecting_area
        expected = {'collections': set([('Benjamin Sisko', '/benjamin-sisko/')]), 'subject_specialists': set([('Jean-Luc Picard', 'Captain of the USS Enterprise', '/jean-luc-picard-public/', '', (), None)]), 'exhibits': set([('Lieutenant Commander Worf', '/lieutenant-commander-worf/')])}
        self.assertEqual(page.get_related(), expected)

    def test_get_related_with_children(self):
        page = self.collecting_area
        related = page.get_related(children=True)
        specialists = set(r[0] for r in related['subject_specialists'])
        collections = set(r[0] for r in related['collections'])
        exhibits = set(r[0] for r in related['exhibits'])
        self.assertTrue('Leonard McCoy' in specialists and 'Jean-Luc Picard' in specialists)
        self.assertTrue('Arne Darvin' in collections and 'Benjamin Sisko' in collections)
        self.assertTrue('Lieutenant Commander Worf' in exhibits and 'Captain Koloth' in exhibits)
        self.assertEqual(len(specialists), 2)
        self.assertEqual(len(collections), 2)
        self.assertEqual(len(exhibits), 2)

    def test_get_features(self):
        page = self.collecting_area
        features = page.get_features()
        self.assertEqual(len(features), 4)
        for f in features:
            self.assertEqual(len(f), 4)
