from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser
from lib_collections.views import collections
from django.core.cache import caches
from django.urls import reverse
from subjects.models import Subject

import time

# Create your tests here.

class test_collex_time(TestCase):
    fixtures = ['test.json']

    def setUp(self):
        self.factory = RequestFactory()
        self.user = AnonymousUser()
        self.startTime = time.time()
        # set up factory request

    def tearDown(self):
        t = time.time() - self.startTime
        print("%s: %.3f" % (self.id(), t))

        caches['default'].clear()
        # clear cache

    def test_view(self):
        request = self.factory.get('/collection/')
        request.user = self.user
        response = collections(request)

        self.assertEqual(response.status_code, 200)

        t = time.time() - self.startTime
        print("%s: %.3f" % (self.id(), t))

    def test_collex(self):
        request = self.factory.get('/collection/?view=collections')
        request.user = self.user
        response = collections(request)

        self.assertEqual(response.status_code, 200)

        t = time.time() - self.startTime
        print("%s: %.3f" % (self.id(), t))

    def test_collex_digital(self):
        request = self.factory.get('/collection/?view=collections&digital=on')
        request.user = self.user
        response = collections(request)

        self.asserEqual(response.status_code, 200)

        t = time.time() - self.startTime
        print("%s: %.3f" % (self.id(), t))

    def test_collex_format(self):
        formats_list = ['Archives & Manuscripts', 'Audio', 'Books & Journals', \
'Images', 'Maps', 'Microform', 'Music Scores', 'Photographs', 'Reference Works', \
'Statistics & Datasets', 'Video']

        for f in formats_list:
            request = self.factory.get('/collection/?view=collections&format=%s' % f)

        t = time.time() - self.startTime
        print("%s: %.3f" % (self.id(), t))

    def test_collex_subjects(self):
        subjects_list = list(Subject.objects.all().values_list("name", flat=True))
        for s in subjects_list:
            request = self.factory.get('/collection/?view=collections&subject=%s' % s)
            request.user = self.user
            response = collections(request)

            self.assertEqual(response.status_code, 200)

        t = time.time() - self.startTime
        print("%s: %.3f" % (self.id(), t))