from django.test import RequestFactory, TestCase
from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTests

from staff.models import StaffPage

from .models import GROUP_PAGE_CONTENT_TYPES, GroupIndexPage, GroupPage


class GroupIndexPageTestCase(WagtailPageTests, TestCase):

    @classmethod
    def setUpTestData(cls):
        """Set up test page hierarchy for GroupIndexPage tests."""
        super().setUpTestData()

        # Create a dedicated test site root for intranet pages
        # (not using the default site since these are Loop/intranet pages)
        root = Page.objects.get(id=1)
        cls.site_root = Page(title="Test Intranet Root", slug="test-intranet")
        root.add_child(instance=cls.site_root)

        # Create a Site for this intranet root so pages have URLs
        cls.site = Site.objects.create(
            hostname="test-intranet.local",
            port=8000,
            root_page=cls.site_root,
            is_default_site=False,
            site_name="Test Intranet",
        )

        cls.root = cls.site_root

        # Create a staff page for page_maintainer and editor fields
        cls.staff = StaffPage(
            title="Test Staff",
            cnetid="teststaff",
            position_title="Test Position",
            live=True,
        )
        cls.root.add_child(instance=cls.staff)
        cls.staff.save_revision().publish()

        # Create main GroupIndexPage
        cls.main_index = GroupIndexPage(
            title="Main Groups",
            slug="main-groups",
            intro="Main groups index",
            page_maintainer=cls.staff,
            editor=cls.staff,
            live=True,
        )
        cls.root.add_child(instance=cls.main_index)
        cls.main_index.save_revision().publish()

        # Create some active groups under main index
        cls.group1 = GroupPage(
            title="Group 1",
            slug="group-1",
            body='[{"type": "paragraph", "value": "Test"}]',
            page_maintainer=cls.staff,
            editor=cls.staff,
            live=True,
        )
        cls.main_index.add_child(instance=cls.group1)
        cls.group1.save_revision().publish()

        cls.group2 = GroupPage(
            title="Group 2",
            slug="group-2",
            body='[{"type": "paragraph", "value": "Test"}]',
            page_maintainer=cls.staff,
            editor=cls.staff,
            live=True,
        )
        cls.main_index.add_child(instance=cls.group2)
        cls.group2.save_revision().publish()

        # Create a subgroup under Group 1
        cls.subgroup1 = GroupPage(
            title="Subgroup 1",
            slug="subgroup-1",
            body='[{"type": "paragraph", "value": "Test"}]',
            page_maintainer=cls.staff,
            editor=cls.staff,
            live=True,
        )
        cls.group1.add_child(instance=cls.subgroup1)
        cls.subgroup1.save_revision().publish()

        # Create a child GroupIndexPage for inactive groups
        cls.inactive_index = GroupIndexPage(
            title="Inactive Groups",
            slug="inactive-groups",
            intro="Inactive groups index",
            page_maintainer=cls.staff,
            editor=cls.staff,
            live=True,
        )
        cls.main_index.add_child(instance=cls.inactive_index)
        cls.inactive_index.save_revision().publish()

        # Create groups under inactive index
        cls.group3 = GroupPage(
            title="Group 3",
            slug="group-3",
            body='[{"type": "paragraph", "value": "Test"}]',
            page_maintainer=cls.staff,
            editor=cls.staff,
            live=True,
        )
        cls.inactive_index.add_child(instance=cls.group3)
        cls.group3.save_revision().publish()

        # Create a subgroup under inactive Group 3
        cls.subgroup2 = GroupPage(
            title="Subgroup 2",
            slug="subgroup-2",
            body='[{"type": "paragraph", "value": "Test"}]',
            page_maintainer=cls.staff,
            editor=cls.staff,
            live=True,
        )
        cls.group3.add_child(instance=cls.subgroup2)
        cls.subgroup2.save_revision().publish()

    def setUp(self):
        """Set up request factory for each test."""
        self.factory = RequestFactory()

    def test_group_index_page_content_type_string_is_expected_format(self):
        page = GroupIndexPage()
        self.assertIn(str(page.content_type), GROUP_PAGE_CONTENT_TYPES)

    def test_group_index_displays_direct_descendants(self):
        """Test that GroupIndexPage displays its direct GroupPage descendants."""
        # Reload from database to get fresh instance with URL
        main_index = GroupIndexPage.objects.get(pk=self.main_index.pk)
        request = self.factory.get("/")
        context = main_index.get_context(request)

        # Check that groups_active_html is in context
        self.assertIn("groups_active_html", context)

        # Check that direct descendants are in the HTML
        html = context["groups_active_html"]
        self.assertIn("Group 1", html)
        self.assertIn("Group 2", html)

    def test_group_index_displays_nested_descendants(self):
        """Test that GroupIndexPage displays nested subgroups."""
        # Reload from database to get fresh instance with URL
        main_index = GroupIndexPage.objects.get(pk=self.main_index.pk)
        request = self.factory.get("/")
        context = main_index.get_context(request)

        html = context["groups_active_html"]
        # Subgroup 1 should appear (it's under Group 1)
        self.assertIn("Subgroup 1", html)

    def test_group_index_excludes_child_index_descendants(self):
        """Test that descendants of child GroupIndexPages are excluded."""
        # Reload from database to get fresh instance with URL
        main_index = GroupIndexPage.objects.get(pk=self.main_index.pk)
        request = self.factory.get("/")
        context = main_index.get_context(request)

        html = context["groups_active_html"]
        # Group 3 and Subgroup 2 should NOT appear (they're under the Inactive Groups index)
        self.assertNotIn("Group 3", html)
        self.assertNotIn("Subgroup 2", html)

    def test_child_group_index_displays_own_descendants(self):
        """Test that child GroupIndexPage displays its own descendants."""
        # Reload from database to get fresh instance with URL
        inactive_index = GroupIndexPage.objects.get(pk=self.inactive_index.pk)
        request = self.factory.get("/")
        context = inactive_index.get_context(request)

        html = context["groups_active_html"]
        # Group 3 and its subgroup should appear in the inactive index
        self.assertIn("Group 3", html)
        self.assertIn("Subgroup 2", html)

    def test_child_group_index_excludes_parent_descendants(self):
        """Test that child GroupIndexPage doesn't show parent's groups."""
        # Reload from database to get fresh instance with URL
        inactive_index = GroupIndexPage.objects.get(pk=self.inactive_index.pk)
        request = self.factory.get("/")
        context = inactive_index.get_context(request)

        html = context["groups_active_html"]
        # Group 1, Group 2, and Subgroup 1 should NOT appear
        self.assertNotIn("Group 1", html)
        self.assertNotIn("Group 2", html)
        self.assertNotIn("Subgroup 1", html)

    def test_alphabetical_ordering(self):
        """Test that groups are displayed in alphabetical order."""
        # Reload main_index from database to get fresh instance
        main_index = GroupIndexPage.objects.get(pk=self.main_index.pk)

        # Create a group that should come first alphabetically
        group_alpha = GroupPage(
            title="Alpha Group",
            slug="alpha-group",
            body='[{"type": "paragraph", "value": "Test"}]',
            page_maintainer=self.staff,
            editor=self.staff,
            live=True,
        )
        main_index.add_child(instance=group_alpha)
        group_alpha.save_revision().publish()

        # Reload again after adding the new group
        main_index = GroupIndexPage.objects.get(pk=self.main_index.pk)
        request = self.factory.get("/")
        context = main_index.get_context(request)

        html = context["groups_active_html"]
        # Alpha Group should appear before Group 1 and Group 2 in the HTML
        alpha_pos = html.find("Alpha Group")
        group1_pos = html.find("Group 1")
        group2_pos = html.find("Group 2")

        self.assertLess(alpha_pos, group1_pos)
        self.assertLess(alpha_pos, group2_pos)


class GroupPageTestCase(TestCase):

    def test_group_page_content_type_string_is_expected_format(self):
        page = GroupPage()
        self.assertIn(str(page.content_type), GROUP_PAGE_CONTENT_TYPES)
