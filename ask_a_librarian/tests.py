from django.test import TestCase, Client
from wagtail.wagtailcore.models import Site
from ask_a_librarian.utils import get_unit_chat_link, get_chat_statuses
from ask_a_librarian.models import AskPage
from units.models import UnitPage
from base.utils import get_hours_and_location
from public.models import StandardPage, PublicRawHTMLPage
from django.http import HttpRequest
from library_website.settings import REGENSTEIN_HOMEPAGE, SSA_HOMEPAGE, MANSUETO_HOMEPAGE, CRERAR_HOMEPAGE, ECKHART_HOMEPAGE, DANGELO_HOMEPAGE, SCRC_HOMEPAGE, PUBLIC_HOMEPAGE, DISSERTATION_HOMEPAGE, SCRC_ASK_PAGE

class TestAskUtils(TestCase):

    # See base.tests to learn how to create this file
    fixtures = ['test.json']

    def setUp(self):
        """
        Common stuff used in multiple test cases. 
        """
        self.ask_pages = AskPage.objects.all()

    def test_get_chat_statuses(self):
        """
        Ensure that statuses are returned for all AskPages except 
        for 1, since, Eckhart uses Crerar's chat widget.
        """
        chat_statuses = get_chat_statuses()
        self.assertEqual(len(self.ask_pages), len(chat_statuses), 'There are AskPages not present in the get_chat_statuses function')
        

    def test_get_unit_chat_link(self):
        """
        Test that pages in the site get the correct ask a librarian 
        link to their corresoinding AskPage and chat widget. Eckhart 
        and SCRC are treated differently since they're circumstances
        are slightly different.
        """
        ask_widgets = set(['law', 'crerar', 'ssa', 'uofc-ask', 'dissertation-office'])

        # Dictionary of tuples where the keys map to the ask_widget_name field  
        # of AskPages. The firs item of the tuple is a mixed dictionary of 
        # location/hours/unit information and the second item of the tuple is 
        # a random url belonging to a page of a given section of the site.
        data = {
            'law': (get_hours_and_location(StandardPage.objects.get(id=DANGELO_HOMEPAGE)), '/law/services/carrelslockers/'),
            'crerar': (get_hours_and_location(StandardPage.objects.get(id=CRERAR_HOMEPAGE)), '/crerar/science-research-services/data-support-services/'),
            'ssa': (get_hours_and_location(StandardPage.objects.get(id=SSA_HOMEPAGE)), '/ssa/about/'),
            'uofc-ask': (get_hours_and_location(StandardPage.objects.get(id=PUBLIC_HOMEPAGE)), '/research/help/offcampus/'),
            'dissertation-office': (get_hours_and_location(StandardPage.objects.get(id=DISSERTATION_HOMEPAGE)), '/research/scholar/phd/students/'),
            'eck': (get_hours_and_location(StandardPage.objects.get(id=ECKHART_HOMEPAGE)), '/eck/mathematics-research-services/'),
            'scrc': (get_hours_and_location(StandardPage.objects.get(id=SCRC_HOMEPAGE)), '/scrc/visiting/'),
        }

        # Normal chat links to regular AskPages
        for item in ask_widgets:
            request = HttpRequest()
            request.path = data[item][1]
            current_site = Site.find_for_request(request)

            a = get_unit_chat_link(data[item][0]['page_unit'], request)
            b = AskPage.objects.filter(ask_widget_name=item).first().relative_url(current_site)

            self.assertEqual(a, b)

        # Eckhart
        request_eck = HttpRequest()
        request_eck.path = data['eck'][1]
        current_site = Site.find_for_request(request_eck)
        eckurl = get_unit_chat_link(data['eck'][0]['page_unit'], request_eck)
        eckask = AskPage.objects.get(id=4646).relative_url(current_site)
        self.assertEqual(eckurl, eckask)


        # SCRC
        request_scrc = HttpRequest()
        request_scrc.path = data['scrc'][1]
        current_site = Site.find_for_request(request_scrc)
        scrcurl = get_unit_chat_link(data['scrc'][0]['page_unit'], request_scrc)
        scrcask = PublicRawHTMLPage.objects.get(id=4127).relative_url(current_site)
        self.assertEqual(scrcurl, scrcask)
