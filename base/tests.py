import json
import sys
from datetime import datetime, timedelta
from io import StringIO

import pandas as pd
from django.contrib.auth.models import Group, User
from django.core import management
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.http import HttpRequest
from django.test import Client, TestCase
from django.urls import clear_url_caches
from file_parsing import is_json
from wagtail.blocks.stream_block import StreamValue
from wagtail.documents.models import Document
from wagtail.models import Page, Site
from wagtailcache.cache import clear_cache

from ask_a_librarian.models import AskPage
from base.models import (
    PAGE_LISTING_MAX_DEPTH,
    BasePage,
    IntranetPlainPage,
    LinkQueueSpreadsheetBlock,
    PageListingBlock,
    build_page_listing,
    get_available_path_under,
)
from base.utils import get_hours_by_id, get_json_for_library
from news.models import NewsPage
from public.models import LocationPage, StandardPage
from staff.models import StaffIndexPage, StaffPage
from units.models import UnitPage

GENERIC_REQUEST_HEADERS = [
    ("HTTP_HOST", "starfleet-academy.com"),
    ("SERVER_PORT", "80"),
    ("SERVER_NAME", "starfleet-academy.com"),
]


# Helper functions
def add_generic_request_meta_fields(request):
    """
    Helper method for adding generic headers to requests.
    Override GENERIC_REQUEST_HEADERS if you need to add
    or alter the META fields provided.

    Args:
        request: HttpRequest object.
    """
    for key, value in GENERIC_REQUEST_HEADERS:
        request.META[key] = value


def create_user_with_privileges(username, password, first_name, last_name, email):
    """
    Create a user that belongs to the proper groups
    to access the intranet.

    Args:
        username: string

        password: string

        first_name: string

        last_name: string

        email: string
    """
    from base.management.commands.create_library_user import Command

    # Create a user
    user = User.objects.create(
        username=username,
        password=password,
        first_name=first_name,
        last_name=last_name,
        email=email,
    )
    user.save()

    # Add user to groups
    groups = Command.REQUIRED_GROUP_NAMES
    library_group = Group.objects.get_or_create(name=groups[1])[0]
    editors_group = Group.objects.get_or_create(name=groups[2])[0]
    library_group.user_set.add(user)
    editors_group.user_set.add(user)

    return user


def loggin_user_with_privileges(user):
    """
    Login a test user that belongs to the proper groups
    to access the intranet.

    Args:
        user: django user object.
    """
    user.client = Client()
    user.client.login(username="geordilaforge", password="broken_visor!")
    return user


def run_report_page_maintainers_and_editors(options):
    """
    Run the report_page_maintainers_and_editors command
    with options.

    Args:
        options: dictionary of options for report_page_maintainers_and_editors.

    Returns:
        string: of stdout captured.
    """
    # Setup the environment
    backup = sys.stdout

    # Capture stdout
    sys.stdout = StringIO()
    management.call_command("report_page_maintainers_and_editors", **options)
    output = sys.stdout.getvalue()

    # Concatonate output
    csv = ""
    csv += output

    # Restore original stdout
    sys.stdout.close()
    sys.stdout = backup

    return csv


def boiler_plate(instance):
    # Delete the default localhost site created by Wagtail migrations
    # to prevent conflicts with our test site
    Site.objects.filter(hostname="localhost").delete()

    # Clear cache after site deletion and before creating new site
    # This ensures Wagtail doesn't use stale cached references
    clear_url_caches()
    cache.clear()
    clear_cache()

    # Create the homepage
    root = Page.objects.get(path="0001")
    instance.homepage = Page(
        slug="welcome-to-starfleet-academy", title="Welcome to Starfleet Academy"
    )
    root.add_child(instance=instance.homepage)

    # Create a site and associate the homepage with it
    instance.site = Site.objects.create(
        hostname="starfleet-academy.com",
        is_default_site=True,
        port=80,
        root_page=instance.homepage,
        site_name="test federation site",
    )

    # Necessary pages
    instance.staff = StaffPage(
        title="Jean-Luc Picard",
        cnetid="picard",
        position_title="Captain of the USS Enterprise",
    )
    instance.homepage.add_child(instance=instance.staff)

    instance.unit = UnitPage(
        title="USS Enterprise (NCC-1701-D)",
        page_maintainer=instance.staff,
        editor=instance.staff,
        display_in_dropdown=True,
    )
    instance.homepage.add_child(instance=instance.unit)

    instance.ask_page = AskPage(
        title="Ask a Betazoid (or don't)",
        page_maintainer=instance.staff,
        editor=instance.staff,
        content_specialist=instance.staff,
        unit=instance.unit,
    )
    instance.homepage.add_child(instance=instance.ask_page)

    instance.building = LocationPage(
        title="Deep Space 9",
        is_building=True,
        short_description="A space station orbiting Bajor.",
        long_description="A space station orbiting Bajor\
        that was called Terok Nor during the occupation.",
        page_maintainer=instance.staff,
        editor=instance.staff,
        content_specialist=instance.staff,
        libcal_library_id=1357,
        unit=instance.unit,
    )
    instance.homepage.add_child(instance=instance.building)

    # Set location property on UnitPage already created
    instance.unit.location = instance.building
    instance.unit.save()

    instance.page = StandardPage(
        title="The Great Link",
        page_maintainer=instance.staff,
        editor=instance.staff,
        content_specialist=instance.staff,
        unit=instance.unit,
        slug="the-great-link-test",
        rich_text="Fallback text.",
        rich_text_heading="Explore",
        rich_text_external_link="https://something.com",
    )
    instance.homepage.add_child(instance=instance.page)


# Tests


class TestUsersAndServingLivePages(TestCase):
    """
    Tests to run on a json dump of the database.

    1. Import a fresh dump of the production DB into your dev site.
    2. Setup your dev sites in the wagtail admin.
    3. Use the following command to get json from the live
       database and move it into the /base/fixters directory:
       python manage.py dumpdata --natural-foreign --natural-primary --exclude wagtailcore.GroupCollectionPermission > test.json
    4. Run the tests.

    Note:
    If you'd like to import the complete database and prune it down to a minimal set of pages for testing,
    you can do something like this:

    from wagtail.models import Page
    from ask_a_librarian.models import AskPage
    from staff.models import StaffPage
    from units.models import UnitPage
    pages = Page.objects.exclude(id__in=[1, 6, 7, 9, 12, 23, 33, 38, 82, 272, 278,
    279, 280, 282, 407, 451, 452, 521, 587, 665, 754, 755, 822, 1207, 1208, 1260,
    1448, 1632, 1669, 1670, 1671, 1672, 1674, 1675, 1677, 1678, 1679, 1707, 1752,
    1753, 1754, 1755, 1756, 1757, 1758, 1779, 1797, 1798, 1816, 1831, 1862, 1871,
    1893, 2165, 2166, 2198, 2226, 2230, 2261, 2281, 2283, 2452, 2455, 2456, 2458,
    2685, 2713, 2714, 2923, 2927, 2970, 2971, 2980, 2981, 3000, 3184, 3185, 3213,
    3314, 3378, 3380, 3392, 3393, 3640, 3643, 3692, 3699, 3961, 4084, 4127, 4186,
    4273, 4317, 4499, 4637, 4646, 4717, 4872, 4873]).not_type((AskPage, StaffPage, UnitPage)).delete()

    from wagtail.documents.models import Document
    Document.objects.all().delete()

    from wagtail.images.models import Image
    Image.objects.exclude(id__in=[626, 1129, 1130]).delete()
    """

    # Load a copy of the production database
    fixtures = ["test.json"]

    def setUp(self):
        # Explicitly clear the cache of site root paths. Normally this would be kept
        # in sync by the Site.save logic, but this is bypassed when the database is
        # rolled back between tests using transactions.
        from django.core.cache import cache

        cache.delete("wagtail_site_root_paths")

        # also need to clear urlresolver caches before/after tests, because we override
        # ROOT_URLCONF in some tests here
        from django.urls import clear_url_caches

        clear_url_caches()

    def tearDown(self):
        from django.urls import clear_url_caches

        clear_url_caches()

    def test_random_news_page(self):
        """
        Test an arbitrary web page. For similar tests look at:
        https://github.com/torchbox/wagtail/blob/master/wagtail
        /wagtailcore/tests/test_page_model.py
        """
        hostname = Site.objects.filter(site_name="Loop")[0].hostname
        news_page = NewsPage.objects.live().first()
        request = HttpRequest()
        add_generic_request_meta_fields(request)
        request.user = User.objects.all().filter(is_staff=True, is_active=True).first()
        request.site = Site.objects.filter(hostname=hostname)
        response = news_page.serve(request)
        self.assertEqual(response.status_code, 200)

    # def test_group_page(self):
    #    """
    #    Test a generic page on the intranet with a logged in
    #    user that belongs to the necessary groups.
    #    """
    #    hostname = Site.objects.filter(site_name='Loop')[0].hostname
    #    user = loggin_user_with_privileges(create_user_with_privileges())
    #    response = user.client.get('/groups/web-content-group/', HTTP_HOST=hostname)
    #    self.assertEqual(response.status_code, 200)

    # def test_all_live_intranet_pages_for_200(self):
    #    """
    #    Make sure all live pages on the intranet return
    #    200 when visited by a normal Library user that
    #    is logged in with the proper groups assigned.
    #    """
    #    site = Site.objects.filter(site_name='Loop')[0]
    #    user = loggin_user_with_privileges(create_user_with_privileges())
    #    pages = site.root_page.get_descendants().live()

    #    for page in pages:
    #        url = page.relative_url(site)
    #        response = user.client.get(page.url, HTTP_HOST=site.hostname)
    #        self.assertEqual(response.status_code, 200, msg='The following url failed: ' + page.url)

    # def test_loop_page_with_anonymous_user(self):
    #    """
    #    Should redirect.
    #    """
    #    hostname = Site.objects.filter(site_name='Loop')[0].hostname
    #    user = AnonymousUser()
    #    user.client = Client()
    #    response = user.client.get('/groups/web-content-group/', HTTP_HOST=hostname)
    #    self.assertEqual(response.status_code, 302)


class TestPageModels(TestCase):
    """
    Test the page model itself.
    """

    def test_page_models_have_subpage_types(self):
        """
        All page content types should have subpage_types
        explicitly set. This test won't tell us if they're
        set correctly but it will make sure we've at least
        done something.
        """
        # We get rid of the first element because it is a wagtailcore.Page
        content_types = Page.allowed_subpage_models()[1:]
        # number_of_content_types = len(content_types)

        no_subpagetypes = set([])
        for page_type in content_types:
            # num = len(page_type.allowed_subpage_models())
            try:
                # self.assertNotEqual(num, number_of_content_types, 'This content type is missing a subpage_types declaration')
                # assert page_type.subpage_types, 'This content type is missing a subpage_types declaration'
                page_type.subpage_types
            except:  # noqa: E722
                no_subpagetypes.add(page_type.__name__)

        self.assertEqual(
            len(no_subpagetypes),
            0,
            "The following content types don't have a subpages_type declaration: "
            + str(no_subpagetypes),
        )

    def test_page_models_have_search_fields(self):
        """
        All page content types should have search_fields.
        This doesn't tell us if we've set them correctly
        but it ensures we've done something.
        """
        # We get rid of the first element because it is a wagtailcore.Page
        content_types = Page.allowed_subpage_models()[1:]
        page_search_fields = Page.search_fields
        base_page_search_fields = BasePage.search_fields
        default_search_fields = set(page_search_fields + base_page_search_fields)
        ignore = set(
            [
                "AlertPage",
                "AlertIndexPage",
                "ConferenceIndexPage",
                "FindingAidsPage",
                "GroupMeetingMinutesIndexPage",
                "GroupReportsIndexPage",
                "HomePage",
                "IntranetFormPage",
                "IntranetHomePage",
                "IntranetUnitsReportsIndexPage",
                "MyLibDashboardPage",
                "ProjectIndexPage",
                "RedirectPage",
                "LoopRedirectPage",
            ]
        )
        no_search_fields = set([])
        for page_type in content_types:
            if (
                not len(set(page_type.search_fields)) > len(default_search_fields)
                and page_type.__name__ not in ignore
            ):
                no_search_fields.add(page_type.__name__)

        self.assertEqual(
            len(no_search_fields),
            0,
            "The following content types don't have a search_fields declaration or their search_field declaration is not extending a base_class search_fields attribute: "
            + str(no_search_fields),
        )


class TestStreamFields(TestCase):

    # Load a copy of the production database
    fixtures = ["test.json"]

    def test_staff_listing_stream_fields(self):
        # get a few pages for the test.
        home_page = Site.objects.first().root_page
        staff_index_page = StaffIndexPage.objects.first()
        alien = StaffPage.objects.live().first()

        try:
            StaffPage.objects.get(cnetid="ignatius").delete()
        except StaffPage.DoesNotExist:
            pass

        # create a fictional StaffPage object for testing.
        staff_page = StaffPage.objects.create(
            cnetid="ignatius",
            depth=staff_index_page.depth + 1,
            path=get_available_path_under(staff_index_page.path),
            slug="ignatius-reilly",
            title="Ignatius Reilly",
        )

        # build a streamfield by hand for testing.
        body = json.dumps(
            [
                {
                    "type": "staff_listing",
                    "value": {
                        "staff_listing": [staff_page.id],
                        "show_photos": False,
                        "show_contact_info": False,
                        "show_subject_specialties": False,
                    },
                }
            ]
        )

        try:
            StandardPage.objects.get(slug="a-standard-page").delete()
        except StandardPage.DoesNotExist:
            pass

        # create a StandardPage under the homepage for testing.
        standard_page = StandardPage.objects.create(
            body=body,
            content_specialist=staff_page,
            depth=home_page.depth + 1,
            editor=alien,
            page_maintainer=staff_page,
            path=get_available_path_under(home_page.path),
            slug="a-standard-page",
            title="A Standard Page",
            unit=UnitPage.objects.get(title="Library"),
        )

        # retrieve the StandardPage and make sure the status code is 200.
        request = HttpRequest()
        add_generic_request_meta_fields(request)
        response = standard_page.serve(request)
        self.assertEqual(response.status_code, 200)

        # delete the StaffPage object. Test again, the status code should still be
        # 200.
        try:
            staff_page.delete()
        except StaffPage.DoesNotExist:
            pass

        response = standard_page.serve(request)
        self.assertEqual(response.status_code, 200)

        # delete the StandardPage.
        try:
            standard_page.delete()
        except StandardPage.DoesNotExist:
            pass


class TestUtilityFunctions(TestCase):
    """
    Utility functions in base/utils.py.
    """

    def test_get_json_for_library(self):
        """
        Should return valid json always. If a bad library id is
        passed a string, 'null' should come back.
        """
        crerar = 1373
        self.assertEqual(
            is_json(json.dumps(get_json_for_library(crerar))), True, "Not valid json"
        )
        self.assertEqual(
            json.dumps(get_json_for_library(999)), "null", "Should be a null json value"
        )

    def test_get_hours_by_id(self):
        """
        Very basic test, needs more.
        """
        crerar = 1373
        assert len(get_hours_by_id(crerar)) > 1
        self.assertEqual(get_hours_by_id(999), "Unavailable")


class TestAssignUnitLocationCommand(TestCase):
    """
    Test cases for the assign_unit_location manage command.
    """

    fixtures = ["test.json"]

    def test_assign_unit_location(self):
        """
        Should exit with a code of 1 if a location or
        unit doesn't exist.
        """
        # Suppress stdout to avoid cluttering test output
        out = StringIO()
        with self.assertRaises(SystemExit) as cm:
            management.call_command("assign_unit_location", str(1), str(2), stdout=out)

        self.assertEqual(cm.exception.code, 1)


class TestPageOwnerReports(TestCase):
    """
    Test cases for the page owner reports command and
    associated views.
    """

    fixtures = ["test.json"]

    # Note: Cannot use setUpTestData() because Command objects contain
    # file handles that aren't picklable (can't be deepcopied)
    def setUp(self):
        from base.management.commands.report_page_maintainers_and_editors import Command

        class Ship(object):
            name = "Enterprise"
            warp = 9

        # Foobar objects to test
        self.c = Command()
        self.ship = Ship()

        self.loop = Site.objects.get(site_name="Loop")
        self.public = Site.objects.get(site_name="Public")

        self.all_live_pages = Page.objects.live()

    def test_get_attr_with_object_attributes(self):
        self.assertEqual(self.c._get_attr(self.ship, "name"), "Enterprise")
        self.assertEqual(self.c._get_attr(self.ship, "warp"), 9)

    def test_get_attr_with_object_missing_attribute(self):
        self.assertEqual(self.c._get_attr(self.ship, "romulans"), "")

    def test_get_pages_return_correct_number_of_pages(self):
        num_pages_loop = (
            Page.objects.get(sites_rooted_here=self.loop)
            .get_descendants()
            .live()
            .count()
            + 1
        )
        num_pages_public = (
            Page.objects.get(sites_rooted_here=self.public)
            .get_descendants()
            .live()
            .count()
            + 1
        )
        get_loop_pages_count = sum(1 for p in self.c._get_pages(None, "Loop", None)) - 1
        get_public_pages_count = (
            sum(1 for p in self.c._get_pages(None, "Public", None)) - 1
        )
        self.assertEqual(get_loop_pages_count, num_pages_loop)
        self.assertEqual(get_public_pages_count, num_pages_public)

    def test_get_pages_with_cnetid_only_returns_pages_with_any_role(self):
        """
        When only the cnetid is filled out pages with any role should
        be returned it it's assigned to the given cnetid. There are 6
        pages in the test db that belong to Locutus of Borg. He is a
        he is a page_maintainor on some, editor on others and
        content_specialist others.
        """
        get_locutus_pages_count = (
            sum(1 for p in self.c._get_pages("locutus", None, None)) - 1
        )
        self.assertEqual(get_locutus_pages_count, 6)

    def test_get_pages_with_cnetid_and_role(self):
        """
        If a cnetid and a role passed, the function should only return
        pages where the given cnetid is assigned to the given role.
        In the test database there are this many pages for the following
        roles that are assigned to Locutus of Borg:

        page_maintainer: 3 pages
        editor: 1 page
        content_specialist: 2 pages
        """
        page_maintainer_in_scope = (
            sum(1 for p in self.c._get_pages("locutus", None, "page_maintainer")) - 1
        )
        editor_in_scope = (
            sum(1 for p in self.c._get_pages("locutus", None, "editor")) - 1
        )
        content_specialist_in_scope = (
            sum(1 for p in self.c._get_pages("locutus", None, "content_specialist")) - 1
        )
        self.assertEqual(page_maintainer_in_scope, 3)
        self.assertEqual(editor_in_scope, 1)
        self.assertEqual(content_specialist_in_scope, 2)

    def test_get_pages_without_cnet_site_or_role_returns_any_and_all_pages(self):
        all_pages_count = self.all_live_pages.count()
        num_pages = sum(1 for p in self.c._get_pages(None, None, None)) - 1
        self.assertEqual(num_pages, all_pages_count)

    def test_main_command_when_no_pages_are_returned(self):
        """
        The user Q doesn't have any pages assigned to him. The command
        should return a nearly blank spreadsheet.
        """
        options = {
            "site": None,
            "cnetid": "q",
            "role": None,
        }
        csv = run_report_page_maintainers_and_editors(options)
        self.assertEqual(csv.strip(), ",".join(self.c.HEADER))


class TestUpdateSiteDataCommand(TestCase):
    """
    Test cases for the update_site_data manage command.
    """

    fixtures = ["test.json"]

    def test_changing_port_alone(self):
        """
        Change the site port to a new one
        """
        management.call_command("update_site_data", "loopdev", "--port=555")
        site_obj = Site.objects.get(hostname="loopdev")
        self.assertEqual(555, site_obj.port)

    def test_changing_hostname_alone(self):
        """
        Change the site hostname to a new one
        """
        management.call_command("update_site_data", "loopdev", "--new_host=lcars")
        site_obj = Site.objects.get(hostname="lcars")
        self.assertEqual("lcars", site_obj.hostname)

    def test_changing_all_options_at_once(self):
        """
        Pass all paramaters at once
        """
        management.call_command(
            "update_site_data", "loopdev", "--new_host=lcars", "--port=8912"
        )
        site_obj = Site.objects.get(hostname="lcars")
        self.assertEqual("lcars", site_obj.hostname)
        self.assertEqual(8912, site_obj.port)

    def test_bad_port_given(self):
        """
        Test what happens when a non-numeric port is given
        """
        self.assertRaises(
            ValueError,
            management.call_command,
            "update_site_data",
            "loopdev",
            "--port=borg",
        )


class LinkQueueSpreadsheetBlockTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create necessary pages
        boiler_plate(cls)

        # Documents
        # Good data, current links
        now = datetime.now()
        later = now + timedelta(days=5)
        sformat = "%m/%d/%Y"
        now_string = now.strftime(sformat)
        later_string = later.strftime(sformat)
        data = {
            "Start Date": ["05/1/2021", later_string, now_string],
            "End Date": ["06/3/2021", now_string, later_string],
            "Link Text": ["The Grand Nagus", "Picard", "A deal is a deal"],
            "URL": [
                "https://foobar.com",
                "https://test.com",
                "https://memory-alpha.fandom.com/wiki/Rules_of_Acquisition",
            ],
        }
        cls.good_document = cls.makeTestingSpreadsheet(
            "documents/test_get_link_queue.xlsx", data, "The Rules of Acquisition"
        )
        cls.good_document.save()

        # Old dates, no current links
        data = {
            "Start Date": ["05/1/2021", "06/2/2021", "07/3/2021"],
            "End Date": ["06/3/2021", "07/4/2021", "08/5/2021"],
            "Link Text": ["The Grand Nagus", "Picard", "A deal is a deal"],
            "URL": [
                "https://foobar.com",
                "https://test.com",
                "https://memory-alpha.fandom.com/wiki/Rules_of_Acquisition",
            ],
        }
        cls.document_expired = cls.makeTestingSpreadsheet(
            "documents/test_link_queue_fallback.xlsx", data, "The Rules of Acquisition"
        )
        cls.document_expired.save()

        # Empty spreadsheet
        cls.path_to_empty_doc = "documents/test_empty.xlsx"
        df = pd.DataFrame()
        df.to_excel("media/" + cls.path_to_empty_doc, index=False)
        cls.empty_document = Document.objects.create(
            title="Empty Spreadsheet", file=cls.path_to_empty_doc
        )
        cls.empty_document.save()

    @classmethod
    def makeTestingSpreadsheet(cls, path_to_file, data, title):
        df = pd.DataFrame(data)
        df.to_excel("media/" + path_to_file, index=False)
        return Document.objects.create(title=title, file=path_to_file)

    def tearDown(self):
        clear_url_caches()
        cache.clear()
        clear_cache()

    def test_clean_invalid_file_extension(self):
        file_path = "documents/invalid_file.doc"
        block = LinkQueueSpreadsheetBlock()
        invalid_document = Document.objects.create(
            title="Wrong File Extension", file=file_path
        )
        invalid_document.save()
        sv = StreamValue(
            stream_block=block,
            stream_data=[
                {
                    "type": "linkqueuespreadsheetblock",
                    "value": [{"type": "spreadsheet", "value": invalid_document.id}],
                }
            ],
            is_lazy=True,
        )
        sv.filename = file_path

        # Assertion should be raised on files that aren't .xlsx
        with self.assertRaises(ValidationError) as cm:
            block.clean(sv)
        ex = cm.exception
        self.assertEqual(ex.messages[0], "Your spreadsheet file must be an .xlsx")

    def test_clean_invalid_spreadsheet_headers(self):
        path_to_file = "documents/test.xlsx"
        block = LinkQueueSpreadsheetBlock()
        data = {
            "Test1": ["Foo", "Foo", "Foo"],
            "Test2": ["Foo", "Foo", "Foo"],
            "Test3": ["Foo", "Foo", "Foo"],
            "Test4": ["Foo", "Foo", "Foo"],
        }
        invalid_document = self.makeTestingSpreadsheet(
            path_to_file, data, "Bad Spreadsheet Headers"
        )
        invalid_document.save()

        sv = StreamValue(
            stream_block=block,
            stream_data=[
                {
                    "type": "linkqueuespreadsheetblock",
                    "value": [{"type": "spreadsheet", "value": invalid_document.id}],
                }
            ],
            is_lazy=True,
        )
        sv.filename = path_to_file
        sv.file = path_to_file

        # Assertion should be raised on spreadsheets that don't have the required headers
        with self.assertRaises(ValidationError) as cm:
            block.clean(sv)
        ex = cm.exception
        self.assertEqual(
            ex.messages[0],
            'Your spreadsheet file must have "Start Date", "End Date", "Link Text", and "URL" column headers',
        )

    def test_clean_empty_spreadsheet(self):
        block = LinkQueueSpreadsheetBlock()
        sv = StreamValue(
            stream_block=block,
            stream_data=[
                {
                    "type": "linkqueuespreadsheetblock",
                    "value": [{"type": "spreadsheet", "value": self.empty_document.id}],
                }
            ],
            is_lazy=True,
        )
        sv.filename = self.path_to_empty_doc
        sv.file = self.path_to_empty_doc

        # Assertion should be raised on spreadsheets that don't have the required headers
        with self.assertRaises(ValidationError) as cm:
            block.clean(sv)
        ex = cm.exception
        self.assertEqual(
            ex.messages[0],
            "Empty spreadsheets are not allowed",
        )

    def test_get_link_queue(self):
        self.page.link_queue = json.dumps(
            [{"type": "spreadsheet", "value": self.good_document.id}]
        )
        self.page.save()

        q = self.page.get_link_queue()
        expected_val = {
            "The Rules of Acquisition": [
                (
                    "https://memory-alpha.fandom.com/wiki/Rules_of_Acquisition",
                    "A deal is a deal",
                )
            ]
        }
        self.assertEqual(q, expected_val)

    def test_link_queue_rich_text_fallback(self):
        fallback_text = "Fallback text."
        request = HttpRequest()
        add_generic_request_meta_fields(request)
        response = self.page.serve(request)

        # Should have fallback text when link queue has not been set
        self.assertContains(response, fallback_text)

        # Should have fallback text when a link queue is set but the dates are old
        self.page.link_queue = json.dumps(
            [{"type": "spreadsheet", "value": self.document_expired.id}]
        )
        self.page.save()
        request = HttpRequest()
        add_generic_request_meta_fields(request)
        response = self.page.serve(request)
        self.assertContains(response, fallback_text)

        # Should not have fallback text when a link queue is set and the dates are current
        self.page.link_queue = json.dumps(
            [{"type": "spreadsheet", "value": self.good_document.id}]
        )
        self.page.save()
        request = HttpRequest()
        add_generic_request_meta_fields(request)
        response = self.page.serve(request)
        self.assertNotContains(response, fallback_text)
        self.assertContains(response, "A deal is a deal")

    def test_empty_spreadsheet_does_not_break_page(self):
        request = HttpRequest()
        add_generic_request_meta_fields(request)
        response = self.page.serve(request)

        # Pages with an empty document should still return a 200
        self.page.link_queue = json.dumps(
            [{"type": "spreadsheet", "value": self.empty_document.id}]
        )
        self.page.save()
        request = HttpRequest()
        add_generic_request_meta_fields(request)
        response = self.page.serve(request)
        self.assertEqual(response.status_code, 200)

        # Pages with a document deleted should still return a 200
        self.empty_document.delete()
        response = self.page.serve(request)
        self.assertEqual(response.status_code, 200)


class PageListingBlockTestCase(TestCase):
    """
    Tests for the "Page Listing" streamfield block and the helper
    that builds its nested data structure.
    """

    @classmethod
    def setUpTestData(cls):
        boiler_plate(cls)

        # A section four levels deep, with a page excluded from menus and an
        # unpublished page, each with a child of their own:
        #
        # section
        # |-- child (in menus)
        # |   `-- grandchild (in menus)
        # |       `-- great_grandchild (in menus)
        # |-- hidden_child (not in menus)
        # |   `-- hidden_grandchild (in menus)
        # `-- draft_child (not live)
        #     `-- draft_grandchild (in menus)
        cls.section = cls.make_page(cls.homepage, "Bajor")
        cls.child = cls.make_page(cls.section, "Bajoran Provisional Government")
        cls.grandchild = cls.make_page(cls.child, "Chamber of Ministers")
        cls.great_grandchild = cls.make_page(cls.grandchild, "First Minister")
        cls.hidden_child = cls.make_page(cls.section, "Obsidian Order", in_menu=False)
        cls.hidden_grandchild = cls.make_page(cls.hidden_child, "Enabran Tain")
        cls.draft_child = cls.make_page(cls.section, "Circle Coup", live=False)
        cls.draft_grandchild = cls.make_page(cls.draft_child, "Jaro Essa")

        # A section on Loop. Loop content types extend BasePage while
        # public ones extend PublicBasePage.
        cls.loop_section = cls.make_loop_page(cls.homepage, "Cardassian Union")
        cls.loop_child = cls.make_loop_page(cls.loop_section, "Detapa Council")

    @classmethod
    def make_page(cls, parent, title, in_menu=True, live=True):
        page = StandardPage(
            title=title,
            content_specialist=cls.staff,
            editor=cls.staff,
            live=live,
            page_maintainer=cls.staff,
            show_in_menus=in_menu,
            unit=cls.unit,
        )
        parent.add_child(instance=page)
        return page

    @classmethod
    def make_loop_page(cls, parent, title):
        page = IntranetPlainPage(
            title=title,
            editor=cls.staff,
            page_maintainer=cls.staff,
            show_in_menus=True,
        )
        parent.add_child(instance=page)
        return page

    def tearDown(self):
        clear_url_caches()
        cache.clear()
        clear_cache()

    def titles(self, listing):
        """
        Flatten a listing into a list of titles for easy comparison.
        """
        titles = []
        for node in listing:
            titles.append(node["title"])
            titles.extend(self.titles(node["children"]))
        return titles

    def block_value(self, root_page=None, depth="1", heading=""):
        """
        The value of a single Page Listing block.
        """
        return {
            "heading": heading,
            "root_page": root_page.id if root_page else None,
            "depth": depth,
        }

    def block_body(self, root_page=None, depth="1", heading=""):
        """
        A streamfield containing nothing but a Page Listing block.
        """
        return json.dumps(
            [
                {
                    "type": "page_listing",
                    "value": self.block_value(root_page, depth, heading),
                }
            ]
        )

    def render_block(self, page, root_page=None, depth="1", heading=""):
        """
        Serve a page with a single Page Listing block in the body and
        return the response. Saves the page without validating it, so
        combinations an editor would be stopped from choosing can be
        rendered too.
        """
        page.body = self.block_body(root_page, depth, heading)
        page.save(clean=False)
        request = HttpRequest()
        add_generic_request_meta_fields(request)
        return page.serve(request)

    def listing_for(self, page, root_page=None, depth="1"):
        """
        The listing a Page Listing block builds when it appears on a
        given page.
        """
        request = HttpRequest()
        add_generic_request_meta_fields(request)
        block = PageListingBlock()
        context = block.get_context(
            block.to_python(self.block_value(root_page, depth)),
            parent_context={"page": page, "request": request},
        )
        return context["pages"]

    def test_one_level_lists_immediate_children_only(self):
        listing = build_page_listing(self.section, 1)
        self.assertEqual(self.titles(listing), [self.child.title])

    def test_depth_is_honored(self):
        listing = build_page_listing(self.section, 2)
        self.assertEqual(
            self.titles(listing), [self.child.title, self.grandchild.title]
        )

    def test_depth_is_clamped_to_the_maximum(self):
        expected = self.titles(build_page_listing(self.section, PAGE_LISTING_MAX_DEPTH))
        self.assertEqual(self.titles(build_page_listing(self.section, 99)), expected)

        # The editor should never be offered a depth beyond the cap either
        choices = dict(PageListingBlock().child_blocks["depth"].field.choices)
        self.assertEqual(
            sorted(choices), [str(n) for n in range(1, PAGE_LISTING_MAX_DEPTH + 1)]
        )

    def test_invalid_depth_falls_back_to_one_level(self):
        expected = self.titles(build_page_listing(self.section, 1))
        for depth in (None, "", "banana", 0, -3):
            self.assertEqual(
                self.titles(build_page_listing(self.section, depth)), expected
            )

    def test_descendants_are_fetched_in_a_single_query(self):
        # Warm the site root paths cache, which page urls are built from
        build_page_listing(self.section, PAGE_LISTING_MAX_DEPTH)

        with self.assertNumQueries(1):
            build_page_listing(self.section, PAGE_LISTING_MAX_DEPTH)

    def test_pages_hidden_from_menus_and_drafts_are_excluded(self):
        listing = build_page_listing(self.section, PAGE_LISTING_MAX_DEPTH)
        titles = self.titles(listing)

        self.assertNotIn(self.hidden_child.title, titles)
        self.assertNotIn(self.draft_child.title, titles)

        # An excluded page takes its own children with it
        self.assertNotIn(self.hidden_grandchild.title, titles)
        self.assertNotIn(self.draft_grandchild.title, titles)

    def test_nesting_structure(self):
        listing = build_page_listing(self.section, 3)

        self.assertEqual(len(listing), 1)
        self.assertEqual(listing[0]["title"], self.child.title)
        self.assertEqual(listing[0]["url"], self.child.url)

        children = listing[0]["children"]
        self.assertEqual([node["title"] for node in children], [self.grandchild.title])
        self.assertEqual(
            [node["title"] for node in children[0]["children"]],
            [self.great_grandchild.title],
        )

    def test_blank_root_page_lists_children_of_the_current_page(self):
        response = self.render_block(self.section, depth="2")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="index-list"')
        self.assertContains(response, self.child.title)
        self.assertContains(response, self.grandchild.title)
        self.assertNotContains(response, self.hidden_child.title)

    def test_root_page_lists_the_chosen_section(self):
        # The listing is rooted at another section, not at the page the
        # block appears on.
        response = self.render_block(self.page, root_page=self.child, depth="1")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.grandchild.title)
        self.assertNotContains(response, self.child.title)

    def test_heading_is_rendered_when_supplied(self):
        heading = "Further Reading"
        response = self.render_block(self.section, heading=heading)
        self.assertContains(response, "<h2>%s</h2>" % heading, html=True)

        response = self.render_block(self.section)
        self.assertNotContains(response, heading)

    def test_empty_section_renders_nothing(self):
        response = self.render_block(self.great_grandchild, heading="Further Reading")

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'class="index-list"')
        self.assertNotContains(response, "Further Reading")

    def test_a_loop_section_cannot_be_saved_on_a_public_page(self):
        self.page.body = self.block_body(root_page=self.loop_section)

        with self.assertRaises(ValidationError) as error:
            self.page.clean()

        self.assertIn("body", error.exception.message_dict)
        self.assertIn(self.loop_section.title, str(error.exception))

    def test_a_public_section_can_be_saved_on_a_public_page(self):
        self.page.body = self.block_body(root_page=self.section)
        self.page.clean()

    def test_a_loop_section_can_be_saved_on_a_loop_page(self):
        self.loop_section.body = self.block_body(root_page=self.loop_section)
        self.loop_section.clean()

    def test_a_loop_section_is_not_listed_on_a_public_page(self):
        # Loop page titles are intranet content. Nothing renders, rather
        # than falling back to the children of the public page.
        response = self.render_block(
            self.page, root_page=self.loop_section, heading="Further Reading"
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'class="index-list"')
        self.assertNotContains(response, self.loop_child.title)
        self.assertNotContains(response, "Further Reading")

    def test_a_loop_section_is_not_listed_without_a_page_to_check(self):
        self.assertEqual(self.listing_for(None, root_page=self.loop_section), [])

    def test_a_loop_section_is_listed_on_a_loop_page(self):
        listing = self.listing_for(self.loop_section, root_page=self.loop_section)
        self.assertEqual(self.titles(listing), [self.loop_child.title])

    def test_a_public_section_is_listed_on_a_loop_page(self):
        # Documenting part of the public site on Loop is fine.
        listing = self.listing_for(self.loop_section, root_page=self.section)
        self.assertEqual(self.titles(listing), [self.child.title])
