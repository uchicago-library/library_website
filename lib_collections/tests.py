from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser
from lib_collections.views import collections
from django.core.cache import caches
from django.urls import reverse
from subjects.models import Subject
from units.models import UnitPage
from public.models import LocationPage

import time

# Create your tests here.

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
