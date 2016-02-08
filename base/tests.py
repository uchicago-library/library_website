from base.utils import get_xml_from_directory_api
from django.test import TestCase, Client
from wagtail.wagtailcore.models import Page, Site
from django.contrib.auth.models import User
from django.http import HttpRequest
from news.models import NewsPage
from django.contrib.auth.models import User, Group
from django.contrib.auth.models import AnonymousUser
from io import StringIO
from lxml import etree
from staff.utils import get_all_library_cnetids_from_directory
from tempfile import NamedTemporaryFile
import subprocess
import sys

# Helper functions
def create_user_with_privileges():
    """
    Create a user that belongs to the proper groups
    to access the intranet.
    """
    from base.management.commands.create_library_user import Command

    # Create a user 
    user = User.objects.create(username='geordilaforge', first_name='Geordi', \
        last_name='La Forge', email='glaforge@starfleet.com')
    user.set_password('broken_visor!')
    user.save()
    
    # Add user to groups
    groups = Command.REQUIRED_GROUP_NAMES
    library_group = Group.objects.get(name=groups[1])
    editors_group = Group.objects.get(name=groups[2])
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

# Tests
class TestUsersAndServingLivePages(TestCase):
    """
    Tests to run on a json dump of the database. 

    1. Import a fresh dump of the production DB into your dev site.
    2. Setup your dev sites in the wagtail admin.
    3. Use the following command to get json from the live
       database and move it into the /base/fixters directory:
       python manage.py dumpdata --natural-foreign --natural-primary  > test.json
    4. Run the tests.
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
        from django.core.urlresolvers import clear_url_caches
        clear_url_caches()

    def tearDown(self):
        from django.core.urlresolvers import clear_url_caches
        clear_url_caches()

    def test_news_party_hat_return_page(self):
        """
        Test an arbitrary web page. For similar tests look at:
        https://github.com/torchbox/wagtail/blob/master/wagtail
        /wagtailcore/tests/test_page_model.py
        """
        hostname = Site.objects.filter(site_name='Loop')[0].hostname
        news_page = Page.objects.get(url_path='/loop/news/party-hat-download/')
        request = HttpRequest()
        request.user = User.objects.get(username='elong')
        request.site = Site.objects.filter(hostname=hostname)
        response = news_page.serve(request)
        self.assertEqual(response.status_code, 200)

    def test_group_page(self):
        """
        Test a generic page on the intranet with a logged in 
        user that belongs to the necessary groups.
        """
        hostname = Site.objects.filter(site_name='Loop')[0].hostname
        user = loggin_user_with_privileges(create_user_with_privileges()) 
        response = user.client.get('/groups/web-content-group/', HTTP_HOST=hostname)
        self.assertEqual(response.status_code, 200)

    def test_all_live_intranet_pages_for_200(self):
        """
        Make sure all live pages on the intranet return 
        200 when visited by a normal Library user that 
        is logged in with the proper groups assigned.
        """
        site = Site.objects.filter(site_name='Loop')[0]
        user = loggin_user_with_privileges(create_user_with_privileges())
        pages = site.root_page.get_descendants().live()

        for page in pages:
            url = page.relative_url(site)
            response = user.client.get(page.url, HTTP_HOST=site.hostname)
            self.assertEqual(response.status_code, 200)

    def test_all_live_public_pages_for_200_with_anonymous_user(self):
        """
        Test all live public pages with an anonymous user.
        """
        site = Site.objects.filter(site_name='Public')[0]
        user = AnonymousUser()
        user.client = Client()
        pages = site.root_page.get_descendants().live()

        for page in pages:
            url = page.relative_url(site)
            response = user.client.get(page.url, HTTP_HOST=site.hostname)
            self.assertEqual(response.status_code, 200)

    def test_loop_page_with_anonymous_user(self):
        """
        Should redirect.
        """
        hostname = Site.objects.filter(site_name='Loop')[0].hostname
        user = AnonymousUser()
        user.client = Client()
        response = user.client.get('/groups/web-content-group/', HTTP_HOST=hostname)
        self.assertEqual(response.status_code, 302)

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
        #number_of_content_types = len(content_types)
 
        no_subpagetypes = set([])
        for page_type in content_types:
            #num = len(page_type.allowed_subpage_models())
            try:
                #self.assertNotEqual(num, number_of_content_types, 'This content type is missing a subpage_types declaration')
                #assert page_type.subpage_types, 'This content type is missing a subpage_types declaration'
                page_type.subpage_types
            except:
                no_subpagetypes.add(page_type.__name__)

        self.assertEqual(len(no_subpagetypes), 0, 'The following content types don\'t have a subpages_type declaration: ' + str(no_subpagetypes))

    def test_page_models_have_search_fields(self):
        """
        All page content types should have search_tables.
        This doesn't tell us if we've set them correctly
        but it ensures we've done something. THIS TEST
        IS BROKEN - IT PASSES WHEN IT SHOULD FAIL!
        """
        # We get rid of the first element because it is a wagtailcore.Page
        content_types = Page.allowed_subpage_models()[1:]
        default_search_fields = set(Page.search_fields)
        no_search_fields = set([])
        for page_type in content_types:
            if not len(set(page_type.search_fields)) > len(default_search_fields):
                no_search_fields.add(page_type.__name__)

        self.assertEqual(len(no_search_fields), 0, 'The following content types don\'t have a search_fields declaration: ' + str(no_search_fields))


