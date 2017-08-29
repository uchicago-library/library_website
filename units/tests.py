from diablo_tests import assert_assertion_error
from django.conf import settings
from django.core import management
from django.test import TestCase, Client, override_settings
from io import StringIO
from unittest.mock import patch
from wagtail.wagtailcore.models import Page, Site

from .models import UnitPage
from .utils import get_quick_num_or_link, get_quick_num_html, get_all_quick_nums_html, get_quick_nums_for_library_or_dept
from library_website.settings import PUBLIC_HOMEPAGE, QUICK_NUMS
from openpyxl import load_workbook
from staff.models import StaffPage
from tempfile import NamedTemporaryFile

import os


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
        self.dlist = [{'label': 'Captain Janeway',   'number': '00100', 'link': None},
                     {'label': 'B\'Elanna Torres',  'number': '11000', 'link': None},
                     {'label': 'Seven of Nine',     'number': '01001', 'link': None}]
        self.dlist_expected = '<td><strong>Captain Janeway</strong> 00100</td><td><strong>B\'Elanna Torres</strong> 11000</td><td><strong>Seven of Nine</strong> 01001</td>'


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


    
    def test_get_quick_nums_for_library_or_dept_output(self):
        """
        Test the output of get_quick_nums_for_library_or_dept.
        """
        client = Client()
        site = Site.objects.filter(is_default_site=True)[0]

        # Override for the QUICK_NUMS constant to use in testing
        with self.settings(QUICK_NUMS = {
                'voyager':
                    self.dlist,
                'enterprise':
                    [{'label': 'Captain Picard',    'number': '11100', 'link': None},
                     {'label': 'Worf Rozhenko',     'number': '00001', 'link': None},
                     {'label': 'Data',              'number': '10111', 'link': None}],
                'defiant':
                    [{'label': 'Benjamin Sisko',    'number': '101001', 'link': None},
                     {'label': 'Quark',             'number': '',       'link': site.root_page.id}],
                'the-university-of-chicago-library':
                    [{'label': 'Captain Long',   'number': '00100', 'link': None},
                     {'label': 'Lieutenant Commander Blair',  'number': '11000', 'link': None}],
            }):

            # Normal quick numbers
            expected = '<td><strong>Captain Picard</strong> 11100</td><td><strong>Worf Rozhenko</strong> 00001</td><td><strong>Data</strong> 10111</td>'
            response = client.get('/about/directory/?view=staff&department=Enterprise', HTTP_HOST=site.hostname)
            request = response.wsgi_request
            html = get_quick_nums_for_library_or_dept(request)
            self.assertHTMLEqual(html, expected)

            # Link instead of number
            expected = '<td><strong>Benjamin Sisko</strong> 101001</td><td><strong><a href="/">Quark</a></strong></td>'
            response = client.get('/about/directory/?view=staff&department=Defiant', HTTP_HOST=site.hostname)
            request = response.wsgi_request
            html = get_quick_nums_for_library_or_dept(request)
            self.assertHTMLEqual(html, expected)

            # Test library parameter
            expected = self.dlist_expected
            response = client.get('/about/directory/?view=staff&library=Voyager', HTTP_HOST=site.hostname)
            request = response.wsgi_request
            html = get_quick_nums_for_library_or_dept(request)
            self.assertHTMLEqual(html, expected)

            # Bad parameter not in dictionary should return the default values for library
            expected = '<td><strong>Captain Long</strong> 00100</td><td><strong>Lieutenant Commander Blair</strong> 11000</td>'
            response = client.get('/about/directory/?view=staff&department=Borg Cube', HTTP_HOST=site.hostname)
            request = response.wsgi_request
            html = get_quick_nums_for_library_or_dept(request)
            self.assertHTMLEqual(html, expected)



    def test_get_quick_nums_for_library_or_dept_with_bad_config(self):
        """
        Bad dictionary missing a required key, should throw an assertion error.
        """
        client = Client()
        site = Site.objects.filter(is_default_site=True)[0]
        response = client.get('/about/directory/?view=staff&department=Voyager', HTTP_HOST=site.hostname) # Must stay outside of the context manager

        with self.settings(QUICK_NUMS = {
                'voyager':
                    self.dlist,
                'enterprise':
                    [{'label': 'Captain Picard',    'number': '11100', 'link': None},
                     {'label': 'Worf Rozhenko',     'number': '00001', 'link': None},
                     {'label': 'Data',              'number': '10111', 'link': None}],
            }):

            request = response.wsgi_request
            self.assertTrue(assert_assertion_error(get_quick_nums_for_library_or_dept, request))


    def test_get_all_quick_nums_html_output(self):
        """
        Test for expected html.
        """
        self.assertHTMLEqual(get_all_quick_nums_html(self.dlist), self.dlist_expected)


class ListUnitsWagtail(TestCase):
    def run_command(self, **options):
        tempfile = NamedTemporaryFile(delete=False, suffix='.xlsx')
        management.call_command('list_units_wagtail', tempfile.name, **options)

        wb = load_workbook(tempfile.name)
        ws = wb.active
        os.unlink(tempfile.name)

        return [[cell.value for cell in row] for row in ws.iter_rows(min_row=2)]

    def setUp(self):
        try:
            welcome = Page.objects.get(path='00010001')
        except:
            root = Page.objects.create(
                depth=1,
                path='0001',
                slug='root',
                title='Root')

            welcome = Page(
                path='00010001',
                slug='welcome',
                title='Welcome')
            root.add_child(instance=welcome)

        staff_person = StaffPage(
            cnetid='staff-person',
            slug='staff-person',
            title='Staff Person')
        welcome.add_child(instance=staff_person)

        some_unit = UnitPage(
            editor=staff_person,
            department_head=staff_person,
            page_maintainer=staff_person,
            slug='some-unit',
            title='Some Unit')
        welcome.add_child(instance=some_unit)

    def test_report_column_count(self):
        records = self.run_command(all='True')
        self.assertEqual(len(records[0]), 4)

    def test_report_record_count(self):
        records = self.run_command(all='True')
        self.assertEqual(len(records), 1)

       
