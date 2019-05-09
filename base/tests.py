import json
import os
import sys
from io import StringIO

from django.contrib.auth.models import AnonymousUser, Group, User
from django.core import management
from django.http import HttpRequest
from django.test import Client, TestCase
from file_parsing import is_json
from wagtail.core.models import Page, Site

from base.models import BasePage, get_available_path_under
from base.utils import get_hours_by_id, get_json_for_library
from news.models import NewsPage
from public.models import StandardPage
from staff.models import StaffIndexPage, StaffPage
from units.models import UnitPage

GENERIC_REQUEST_HEADERS = [
    ('HTTP_HOST', 'foobartest.com'), ('SERVER_PORT', '80'),
    ('SERVER_NAME', 'dungeon')
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


def create_user_with_privileges(
    username, password, first_name, last_name, email
):
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
        email=email
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
    user.client.login(username='geordilaforge', password='broken_visor!')
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
    management.call_command('report_page_maintainers_and_editors', **options)
    output = sys.stdout.getvalue()

    # Concatonate output
    csv = ''
    csv += output

    # Restore original stdout
    sys.stdout.close()
    sys.stdout = backup

    return csv


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

    from wagtail.core.models import Page
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
    fixtures = ['test.json']

    def setUp(self):
        # Explicitly clear the cache of site root paths. Normally this would be kept
        # in sync by the Site.save logic, but this is bypassed when the database is
        # rolled back between tests using transactions.
        from django.core.cache import cache
        cache.delete('wagtail_site_root_paths')

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
        hostname = Site.objects.filter(site_name='Loop')[0].hostname
        news_page = NewsPage.objects.live().first()
        request = HttpRequest()
        add_generic_request_meta_fields(request)
        request.user = User.objects.all().filter(
            is_staff=True, is_active=True
        ).first()
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

    def test_all_live_public_pages_for_200_or_redirect_with_anonymous_user(
        self
    ):
        """
        Test all live public pages with an anonymous user.
        Most pages should return a 200, however, the redirect
        page will return a 301 and some custom views return
        a 302. Nothing should return a 404.
        """
        if 'TRAVIS' not in os.environ:
            site = Site.objects.filter(site_name='Public')[0]
            user = AnonymousUser()
            user.client = Client()
            pages = site.root_page.get_descendants().live()
            possible = set([200, 301, 302])

            for page in pages:
                try:
                    response = user.client.get(
                        page.url, HTTP_HOST=site.hostname
                    )
                    self.assertEqual(
                        response.status_code in possible,
                        True,
                        msg=page.url + ' returned a ' +
                        str(response.status_code)
                    )
                except:
                    print(page.relative_url(site) + ' has a problem')
                    raise

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
            except:
                no_subpagetypes.add(page_type.__name__)

        self.assertEqual(
            len(no_subpagetypes), 0,
            'The following content types don\'t have a subpages_type declaration: '
            + str(no_subpagetypes)
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
        default_search_fields = set(
            page_search_fields + base_page_search_fields
        )
        ignore = set(
            [
                'AlertPage', 'AlertIndexPage', 'ConferenceIndexPage',
                'FindingAidsPage', 'GroupMeetingMinutesIndexPage',
                'GroupReportsIndexPage', 'HomePage', 'IntranetFormPage',
                'IntranetHomePage', 'IntranetUnitsReportsIndexPage',
                'ProjectIndexPage', 'RedirectPage'
            ]
        )
        no_search_fields = set([])
        for page_type in content_types:
            if not len(set(page_type.search_fields)) > len(
                default_search_fields
            ) and page_type.__name__ not in ignore:
                no_search_fields.add(page_type.__name__)

        self.assertEqual(
            len(no_search_fields), 0,
            'The following content types don\'t have a search_fields declaration or their search_field declaration is not extending a base_class search_fields attribute: '
            + str(no_search_fields)
        )


class TestStreamFields(TestCase):

    # Load a copy of the production database
    fixtures = ['test.json']

    def test_staff_listing_stream_fields(self):
        # get a few pages for the test.
        home_page = Site.objects.first().root_page
        staff_index_page = StaffIndexPage.objects.first()
        alien = StaffPage.objects.live().first()

        try:
            StaffPage.objects.get(cnetid='ignatius').delete()
        except StaffPage.DoesNotExist:
            pass

        # create a fictional StaffPage object for testing.
        staff_page = StaffPage.objects.create(
            cnetid='ignatius',
            depth=staff_index_page.depth + 1,
            path=get_available_path_under(staff_index_page.path),
            slug='ignatius-reilly',
            title='Ignatius Reilly'
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
                        "show_subject_specialties": False
                    }
                }
            ]
        )

        try:
            StandardPage.objects.get(slug='a-standard-page').delete()
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
            unit=UnitPage.objects.get(title="Library")
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
            is_json(json.dumps(get_json_for_library(crerar))), True,
            'Not valid json'
        )
        self.assertEqual(
            json.dumps(get_json_for_library(999)), 'null',
            'Should be a null json value'
        )

    def test_get_hours_by_id(self):
        """
        Very basic test, needs more.
        """
        crerar = 1373
        assert (len(get_hours_by_id(crerar)) > 1)
        self.assertEqual(get_hours_by_id(999), 'Unavailable')


class TestAssignUnitLocationCommand(TestCase):
    """
    Test cases for the assign_unit_location manage command.
    """
    fixtures = ['test.json']

    def test_assign_unit_location(self):
        """
        Should exit with a code of 1 if a location or
        unit doesn't exist.
        """
        with self.assertRaises(SystemExit) as cm:
            management.call_command('assign_unit_location', str(1), str(2))

        self.assertEqual(cm.exception.code, 1)


class TestPageOwnerReports(TestCase):
    """
    Test cases for the page owner reports command and
    associated views.
    """
    fixtures = ['test.json']

    def setUp(self):
        from base.management.commands.report_page_maintainers_and_editors import Command

        class Ship(object):
            name = 'Enterprise'
            warp = 9

        # Foobar objects to test
        self.c = Command()
        self.ship = Ship()

        self.loop = Site.objects.get(site_name='Loop')
        self.public = Site.objects.get(site_name='Public')

        self.all_live_pages = Page.objects.live()

    def test_get_attr_with_object_attributes(self):
        self.assertEqual(self.c._get_attr(self.ship, 'name'), 'Enterprise')
        self.assertEqual(self.c._get_attr(self.ship, 'warp'), 9)

    def test_get_attr_with_object_missing_attribute(self):
        self.assertEqual(self.c._get_attr(self.ship, 'romulans'), '')

    def test_get_pages_return_correct_number_of_pages(self):
        num_pages_loop = Page.objects.get(sites_rooted_here=self.loop
                                          ).get_descendants().live().count() + 1
        num_pages_public = Page.objects.get(
            sites_rooted_here=self.public
        ).get_descendants().live().count() + 1
        get_loop_pages_count = sum(
            1 for p in self.c._get_pages(None, 'Loop', None)
        )
        get_public_pages_count = sum(
            1 for p in self.c._get_pages(None, 'Public', None)
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
        get_locutus_pages_count = sum(
            1 for p in self.c._get_pages('locutus', None, None)
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
        page_maintainer_in_scope = sum(
            1 for p in self.c._get_pages('locutus', None, 'page_maintainer')
        )
        editor_in_scope = sum(
            1 for p in self.c._get_pages('locutus', None, 'editor')
        )
        content_specialist_in_scope = sum(
            1 for p in self.c._get_pages('locutus', None, 'content_specialist')
        )
        self.assertEqual(page_maintainer_in_scope, 3)
        self.assertEqual(editor_in_scope, 1)
        self.assertEqual(content_specialist_in_scope, 2)

    def test_get_pages_without_cnet_site_or_role_returns_any_and_all_pages(
        self
    ):
        all_pages_count = self.all_live_pages.count()
        num_pages = sum(1 for p in self.c._get_pages(None, None, None))
        self.assertEqual(num_pages, all_pages_count)

    def test_main_command_when_no_pages_are_returned(self):
        """
        The user Q doesn't have any pages assigned to him. The command
        should return a nearly blank spreadsheet.
        """
        options = {
            'site': None,
            'cnetid': 'q',
            'role': None,
        }
        csv = run_report_page_maintainers_and_editors(options)
        self.assertEqual(csv.strip(), ','.join(self.c.HEADER))
