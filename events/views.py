from django.shortcuts import render
from .utils import get_events
from public.models import StandardPage
from library_website.settings import PUBLIC_HOMEPAGE
from base.utils import get_hours_and_location
from ask_a_librarian.utils import get_chat_status, get_chat_status_css, get_unit_chat_link

import calendar
import datetime

def events(request):
    start_str = request.GET.get('start', None)
    if start_str:
        start = datetime.datetime.strptime(start_str, '%Y-%m-%d')
    else:
        start = datetime.date.today()

    # get start and stop dates, along with previous start and next start dates. 
    number_of_days_this_month = calendar.monthrange(start.year, start.month)[1]
    stop = start + datetime.timedelta(days=number_of_days_this_month - 1)

    if start.month == 1:
        number_of_days_last_month = calendar.monthrange(start.year - 1, 12)[1]
    else:
        number_of_days_last_month = calendar.monthrange(start.year, start.month - 1)[1]
    previous_start = start - datetime.timedelta(days=number_of_days_last_month)
    next_start = stop + datetime.timedelta(days=1)

    university_url = 'http://events.uchicago.edu/widgets/rss.php?key=47866f880d62a4f4517a44381f4a990d&id=48'
    ttrss_url = 'http://www3.lib.uchicago.edu/tt-rss/public.php?op=rss&id=-3&key=8idjnk57e2a0063541d'

    entries = get_events(university_url, ttrss_url, start, stop)

    # Page context variables for templates
    home_page = StandardPage.objects.live().get(id=PUBLIC_HOMEPAGE)
    location_and_hours = get_hours_and_location(home_page)
    location = str(location_and_hours['page_location'])
    unit = location_and_hours['page_unit']
    
    return render(request, 'events/events_index_page.html', {
        'breadcrumb_div_css': 'col-md-12 breadcrumbs hidden-xs hidden-sm',
        'content_div_css': 'container body-container col-xs-12 col-lg-11 col-lg-offset-1',
        'entries': entries,
        'next_link': next_start.strftime('%Y-%m-%d'),
        'previous_link': previous_start.strftime('%Y-%m-%d'),
        'start': start.strftime('%Y-%m-%d'),
        'start_label': start.strftime('%B %d, %Y').replace(' 0', ' '),
        'stop': stop.strftime('%Y-%m-%d'),
        'stop_label': stop.strftime('%B %d, %Y').replace(' 0', ' '),
        'page_unit': str(unit),
        'page_location': location,
        'address': location_and_hours['address'],
        'chat_url': get_unit_chat_link(unit, request),
        'chat_status': get_chat_status('uofc-ask'),
        'chat_status_css': get_chat_status_css('uofc-ask'),
        'hours_page_url': home_page.get_hours_page(request),
        'self': {
            'title': 'Library Events'
        },
    })
