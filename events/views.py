from django.shortcuts import render
from .utils import get_flat_entries, group_entries, get_xml_from_university_event_calendar
from public.models import StandardPage
from library_website.settings import PUBLIC_HOMEPAGE
from base.utils import get_hours_and_location
from ask_a_librarian.utils import get_chat_status, get_chat_status_css, get_unit_chat_link

import calendar
import datetime

def events(request):
    view = request.GET.get('view', None)
    if not view:
        view = 'day'

    start = request.GET.get('start', None)
    if start:
        start = datetime.datetime.strptime(start, '%Y-%m-%d')
    else:
        start = datetime.date.today()

    # get info from the event calendar as a list of lists.
    x = get_xml_from_university_event_calendar()
    entries = group_entries(get_flat_entries(x))

    # adjust start and stop dates, depending on whether the view is for a single day,
    # a week or a month. 

    # get the date as a date object for week and month calculations.
    d = start
    if view == 'day':
        stop = start
        previous_start = start - datetime.timedelta(days=1)
        next_start = start + datetime.timedelta(days=1)
    elif view == 'week':
        start = d - datetime.timedelta(days=d.weekday())
        stop = start + datetime.timedelta(days=6)
        previous_start = start - datetime.timedelta(days=7)
        next_start = start + datetime.timedelta(days=7)
    elif view == 'month':
        start = d - datetime.timedelta(days=d.day - 1)
        number_of_days_in_month = calendar.monthrange(d.year, d.month)[1]
        stop = start + datetime.timedelta(days=number_of_days_in_month - 1)

        if d.month == 1:
            number_of_days_last_month = calendar.monthrange(d.year - 1, 12)[1]
        else:
            number_of_days_last_month = calendar.monthrange(d.year, d.month - 1)[1]
        previous_start = start - datetime.timedelta(days=number_of_days_last_month)
        next_start = stop + datetime.timedelta(days=1)

    # only pass along the entries that make sense for this date range. 
    entries_out = []
    i = 0
    while i < len(entries):
        if entries[i][0] >= start.strftime('%Y-%m-%d') and entries[i][0] <= stop.strftime('%Y-%m-%d'):
            entries_out.append(entries[i])
        i = i + 1

    next_link = '#'
    previous_link = '#'

    # Page context variables for templates
    home_page = StandardPage.objects.live().get(id=PUBLIC_HOMEPAGE)
    location_and_hours = get_hours_and_location(home_page)
    location = str(location_and_hours['page_location'])
    unit = location_and_hours['page_unit']
    
    return render(request, 'events/events_index_page.html', {
        'content_div_css': 'container body-container col-xs-12 col-lg-11 col-lg-offset-1',
        'entries': entries_out,
        'next_link': next_start.strftime('%Y-%m-%d'),
        'previous_link': previous_start.strftime('%Y-%m-%d'),
        'start': start.strftime('%Y-%m-%d'),
        'start_label': start.strftime('%B %d, %Y').replace(' 0', ' '),
        'stop': stop.strftime('%Y-%m-%d'),
        'view': view,
        'page_unit': str(unit),
        'page_location': location,
        'address': location_and_hours['address'],
        'chat_url': get_unit_chat_link(unit, request),
        'chat_status': get_chat_status('uofc-ask'),
        'chat_status_css': get_chat_status_css('uofc-ask'),
        'hours_page_url': home_page.get_hours_page(request),
    })
