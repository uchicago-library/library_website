from django.test import TestCase, Client
from wagtail.wagtailcore.models import Page, Site
from django.contrib.auth.models import User
from django.http import HttpRequest
from news.models import NewsPage
from django.contrib.auth.models import User, Group
from django.contrib.auth.models import AnonymousUser
import sys

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


class TestLivePages(TestCase):
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

