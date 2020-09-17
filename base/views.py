import datetime
import json

from ask_a_librarian.utils import (
    get_chat_status, get_chat_status_and_css, get_chat_status_css,
    get_unit_chat_link
)
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from events.utils import flatten_events, get_events
from library_website.settings import PUBLIC_HOMEPAGE, UC_EVENTS_FEED
from public.models import StandardPage
from units.utils import get_default_unit
from wagtail.core.models import Site

from base.utils import (
    get_building_hours_and_lid, get_hours_and_location, get_json_hours_by_id
)


def get_libcalid(request):
    """
    Helper method for parsing libcal id from a request.

    Args:
        request, object

    Returns:
        string representing a libcal id or None
    """
    try:
        return request.GET['libcalid']
    except (KeyError):
        pass
    return None


def json_hours(request):
    """
    View for rendering hours as json.
    """
    current_site = Site.find_for_request(request)
    libcalid = get_libcalid(request)
    if request.method == 'GET':
        if request.GET.get('fallback'):
            return JsonResponse(
                {
                    'llid': get_default_unit().location.libcal_library_id,
                }
            )
        elif libcalid != 'undefined':
            all_building_hours = json.dumps(
                get_building_hours_and_lid(current_site)
            )
            return JsonResponse(
                {
                    'all_building_hours':
                    all_building_hours,
                    'current_hours':
                    get_json_hours_by_id(int(libcalid), all_building_hours),
                    'llid':
                    libcalid,
                    'llid_fallback':
                    get_default_unit().location.libcal_library_id,
                }
            )
        return JsonResponse({})


def json_events(request):
    """
    View for rendering events feed data as json.

    Parameters:
        request: e.g., request.GET['feed'] = 'http://www3.lib.uchicago.edu/tt-rss/public.php?op=rss&id=library&key=oxj4em577573f09bc56'
    """
    if request.method == 'GET':
        ttrss_url = request.GET['feed']

        n = datetime.datetime.now()
        return JsonResponse(
            {
                'events':
                flatten_events(
                    get_events(
                        UC_EVENTS_FEED, ttrss_url, n,
                        n + relativedelta(years=1), False
                    )
                )
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
        return JsonResponse({
            'chat_status': status[0],
            'chat_css': status[1],
        })


def external_include(request):
    """
    CSS, headers and footers for external sites like guides.lib or sfx.lib.
    Make hrefs absolute.
    """
    callback = request.GET.get('callback', None)
    include = request.GET.get('include', None)

    # Variables to use in context
    home_page = StandardPage.objects.live().get(id=PUBLIC_HOMEPAGE)
    location_and_hours = get_hours_and_location(home_page)
    llid = home_page.get_granular_libcal_lid(home_page.unit)
    location = str(location_and_hours['page_location'])
    unit = location_and_hours['page_unit']

    if include in ('css', 'js', 'header', 'footer'):
        response = render(
            request,
            'base/includes/{}.html'.format(include),
            {
                'prefix': '{}://{}'.format(request.scheme, request.get_host),
                'address': location_and_hours['address'],
                'chat_url': get_unit_chat_link(unit, request),
                'chat_status': get_chat_status('uofc-ask'),
                'chat_status_css': get_chat_status_css('uofc-ask'),
                'hours_page_url': home_page.get_hours_page(request),
                'libcalid': llid,
                'page_unit': str(location_and_hours['page_unit']),
                'page_location': location,
                'site_url': request.scheme + '://' + request.get_host(),
            },
        )

        def absolute_url(href):
            """
            Helper function to make links absolute.
            """
            protocol = '{}://'.format(request.scheme)
            if href.startswith('http://') or href.startswith('https://'):
                protocol = ''
            domain = request.get_host()
            if not href.startswith('/'):
                domain = ''
            return '{}{}{}'.format(protocol, domain, href)

        soup = BeautifulSoup(response.content, 'html.parser')
        for a in soup.find_all('a'):
            a['href'] = absolute_url(a['href'])
        for img in soup.find_all('img'):
            img['src'] = absolute_url(img['src'])
        for link in soup.find_all('link'):
            link['href'] = absolute_url(link['href'])
        for sc in soup.find_all('script'):
            sc['src'] = absolute_url(sc['src'])
        response.content = str(soup)
        if callback:
            return HttpResponse(
                '{}({});'.format(
                    callback, json.dumps(response.content.decode('utf-8'))
                ), 'application/javascript'
            )
        else:
            return response
    else:
        raise ValueError
