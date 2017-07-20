from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser
from lib_collections.views import collections

import time

# Create your tests here.

class test_collex_time(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = AnonymousUser()
        self.time = Time.time()
        # set up factory request

    def tearDown(self):
        # clear cache

    def test_view(self):
        request = self.factory.get(reverse('collex'))
        response = collections(request)

        assertEqual(response.httpResponse, 200)

    def test_collex(self):
        request = self.factory.get(reverse('collex', 'view=collex'))
        request.user = self.user

        response = collections(view)