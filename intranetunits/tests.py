from django.test import TestCase

from .models import (
    INTRANET_UNIT_PAGE_CONTENT_TYPES,
    IntranetUnitsIndexPage,
    IntranetUnitsPage,
)


class IntranetUnitsIndexPageTestCase(TestCase):

    def test_intranet_units_index_page_content_type_string_is_expected_format(self):
        page = IntranetUnitsIndexPage()
        self.assertIn(str(page.content_type), INTRANET_UNIT_PAGE_CONTENT_TYPES)


class IntranetUnitsPageTestCase(TestCase):

    def test_intranet_units_page_content_type_string_is_expected_format(self):
        page = IntranetUnitsPage()
        self.assertIn(str(page.content_type), INTRANET_UNIT_PAGE_CONTENT_TYPES)
