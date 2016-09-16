from django.test import TestCase, Client
from units.utils import get_quick_num_or_link, get_quick_num_html, get_quick_nums_for_library_or_dept
from library_website.settings import PUBLIC_HOMEPAGE, QUICK_NUMS
from wagtail.wagtailcore.models import Site
from diablo_tests import assert_assertion_error


class TestQuickNumberUtils(TestCase):
    """
    Tests for utilities used for adding quick numbers
    to the public staff directory.
    """

    fixtures = ['test.json']

    def setUp(self):
        """
        Reusable stuff.
        """
        self.quick_num = {'label': 'Foobar', 'number': '773-702-8740', 'link': None}
        self.quick_link = {'label': 'Foobar', 'number': '', 'link': PUBLIC_HOMEPAGE}


    def test_get_quick_num_or_link(self):
        """
        Make sure the proper exceptions are raised when the input
        is bad and that the proper data is returned wheninput is good.
        """

        # For testing dict keys
        a = {'text': 'Foobar', 'number': '773-702-8740', 'link': None}
        b = {'label': 'Foobar', 'link': None}

        # For testing dict key -> values
        c = {'label': '', 'number': '773-702-8740', 'link': None}
        d = {'label': 'Foobar', 'number': '773-702-8740', 'link': '/'}

        # For testing return values
        e = {'label': 'Foobar', 'number': '773-702-8740', 'link': None}
        f = {'label': 'Foobar', 'number': '', 'link': PUBLIC_HOMEPAGE}
        g = {'label': 'Foobar', 'number': '', 'link': None}

        # Test dict keys
        self.assertTrue(assert_assertion_error(get_quick_num_or_link, a))
        self.assertTrue(assert_assertion_error(get_quick_num_or_link, b))

        # Test dict key -> values
        self.assertTrue(assert_assertion_error(get_quick_num_or_link, c))
        self.assertTrue(assert_assertion_error(get_quick_num_or_link, d))

        # Test return values
        self.assertEqual(get_quick_num_or_link(e), (0, 'Foobar', '773-702-8740'))
        self.assertEqual(get_quick_num_or_link(f), (1, 'Foobar', '/'))
        self.assertRaises(ValueError, get_quick_num_or_link, g)


    def test_get_quick_num_html(self):
        """
        Test the expected HTML output.
        """
        # Expected HTML
        expected_num = '<td><strong>Foobar</strong>773-702-8740</td>'
        expected_link = '<td><strong><a href="/">Foobar</a></strong></td>'

        # Returned HTML
        quick_num_html = get_quick_num_html(get_quick_num_or_link(self.quick_num))
        quick_link_html = get_quick_num_html(get_quick_num_or_link(self.quick_link))

        # Test HTML
        self.assertHTMLEqual(quick_num_html, expected_num)
        self.assertHTMLEqual(quick_link_html, expected_link)


    def test_quick_num_base_config(self):
        """
        Run the current configuration for quicknumbers found 
        in the base config. This tests the QUICK_NUMS constant.
        No exceptions should be raised.
        """
        for library in QUICK_NUMS:
            for number in QUICK_NUMS[library]:
                get_quick_num_or_link(number)


    def test_get_quick_nums_for_library_or_dept(self):
        """
        TODO:
        """
        client = Client()
        site = Site.objects.filter(is_default_site=True)[0]
        response = client.get('/about/directory/?view=staff&department=D\'Angelo+Law+Library', HTTP_HOST=site.hostname)
        request = response.wsgi_request
        get_quick_nums_for_library_or_dept(request)
