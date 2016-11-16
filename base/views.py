from dateutil.relativedelta import relativedelta
from django.shortcuts import render
from django.http import JsonResponse
import json
from base.utils import get_all_building_hours, get_hours_and_location, get_json_hours_by_id, get_building_hours_and_lid, get_news
from events.utils import get_events
from units.utils import get_default_unit
from ask_a_librarian.utils import get_chat_status_and_css
import datetime
import urllib
from wagtail.wagtailcore.models import Site

def breadcrumbs(request):
    breadcrumbs = [{
        "href": "/",
        "text": "Home"
    }]

    path_components = [component for component in request.path.split('/') if component]
    page, args, kwargs = request.site.root_page.specific.route(request, path_components)
    while page:
        breadcrumbs.append({
            "href": page.url,
            "text": page.title
        })
        if hasattr(page, 'parent'):
            page = page.parent
        else:
            break

    return breadcrumbs


def json_hours(request):
    """
    View for rendering hours as json. 
    """
    current_site = Site.find_for_request(request)
    if request.method == 'GET':
        if request.GET.get('fallback'):
            fallback = request.GET['fallback']
            return JsonResponse(
                {
                    'llid': get_default_unit().location.libcal_library_id,
                }
            )
        else:
            libcalid = request.GET['libcalid']
            all_building_hours = json.dumps(get_building_hours_and_lid(current_site))
            return JsonResponse(
                {
                    'all_building_hours': all_building_hours,
                    'current_hours': get_json_hours_by_id(int(libcalid), all_building_hours),
                    'llid': libcalid,
                    'llid_fallback': get_default_unit().location.libcal_library_id,
                }
            )


def json_events(request):
    """
    View for rendering events feed data as json.
    """
    if request.method == 'GET':
        # e.g. http://www3.lib.uchicago.edu/tt-rss/public.php?op=rss&id=library&key=oxj4em577573f09bc56
        ttrss_url = request.GET['feed']

        # need xml for this. 
        university_url = 'http://events.uchicago.edu/widgets/rss.php?key=47866f880d62a4f4517a44381f4a990d&id=48'

        n = datetime.datetime.now()
        events = get_events(university_url, ttrss_url, n, n + relativedelta(years=1), False)

        def flatten_events(events): 
            events_out = []
            for date_event in reversed(events):
                for story in reversed(date_event[1]):
                    events_out.append([story['title'], story['link'], story['date_label'], story['time_label']])
                    if len(events_out) == 3:
                        return events_out
            return events_out

        return JsonResponse(
            {
                'events': flatten_events(events)
            }
        )


def json_news(request):
    """
    View for rendering news feed data as json.
    """
    if request.method == 'GET':
        feed = request.GET['feed']
        return JsonResponse(
            {
                'news': get_news(feed),
            }
        )


def chat_status(request):
    """
    View for retreiving the chat status for 
    Ask a Librarian pages. Returns json.
    """
    if request.method == 'GET':
        ask_name = request.GET['name']
        status = get_chat_status_and_css(ask_name)
        return JsonResponse(
            {
                'chat_status': status[0],
                'chat_css': status[1],
            }
        )


