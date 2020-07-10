from django.test import TestCase

from .models import GROUP_PAGE_CONTENT_TYPES, GroupIndexPage, GroupPage


class GroupIndexPageTestCase(TestCase):

    def test_group_index_page_content_type_string_is_expected_format(self):
        page = GroupIndexPage()
        self.assertIn(str(page.content_type), GROUP_PAGE_CONTENT_TYPES)


class GroupPageTestCase(TestCase):

    def test_group_page_content_type_string_is_expected_format(self):
        page = GroupPage()
        self.assertIn(str(page.content_type), GROUP_PAGE_CONTENT_TYPES)
