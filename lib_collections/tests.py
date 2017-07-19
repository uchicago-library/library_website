from django.test import TestCase

# Create your tests here.

class test_collex_time():
    def setUp(self):
        # set up factory request

    def tearDown(self):
        # clear cache

    def test_collex(self):
        response = collections(request)

        assertEqual(response.httpResponse, 200)