import json

from django.test import Client, TestCase, override_settings
from django.urls import reverse

from item_servlet.utils import (
    get_auth,
    get_holdings,
    get_instances,
    get_item,
    get_location,
)
from item_servlet.views import parse_data


class TestItemServletView(TestCase):
    """
    Test the item servlet.
    """

    def setUp(self):
        """
        Reusable code.
        """
        self.client = Client()
        self.dict_keys = [
            'title',
            'location',
            'internalLocation',
            'callNumber',
            'callNumberPrefix',
            'copyNumber',
            'volumeNumber',
            'author',
            'bibId',
            'barcode',
            'publisher',
            'placePublished',
            'dateIssued',
            'edition',
            'issn',
            'isbn',
            'linking_issn',
        ]

    def test_item_servlet_with_no_params(self):
        """
        Should always be up, give a 200 and serve JSON.
        """
        response = self.client.get(reverse('item-servlet'))
        response.status_code == 200
        content = json.loads(response.content)
        for key in self.dict_keys:
            self.assertTrue(key in content)

    def test_parse_data_with_bad_response(self):
        """
        Even with no instances, item, locaiton, bib or barcode
        we should get a dictionary with standard keys.
        """
        data = parse_data({}, {}, {})
        for key in self.dict_keys:
            self.assertTrue(key in data)


@override_settings(
    FOLIO_USERNAME='Picard',
    FOLIO_PASSWORD='BeverlyCrusher',
    FOLIO_TENANT='Enterprise',
    FOLIO_BASE_URL='https://siufhsari34hriwhrfishfksjfhnsf.com',
)
class TestItemServletUtils(TestCase):
    """
    Test utility functions.
    """

    def test_get_auth_with_bad_data(self):
        auth = get_auth()
        self.assertTrue(auth == {"x-okapi-token": ''})

    def test_get_instances_with_bad_data(self):
        instances = get_instances('badbib', 'badtoken')
        self.assertTrue(instances == {})

    def test_get_holdings_with_bad_data(self):
        holdings = get_holdings('badinstanceid', 'badtoken')
        self.assertTrue(holdings == {})

    def test_get_item_with_bad_data(self):
        item = get_item('badbarcode', 'badtoken')
        self.assertTrue(item == {})

    def test_get_location_with_bad_data(self):
        loc = get_location('badlocationid', 'badtoken')
        self.assertTrue(loc == {})
