from django.shortcuts import render
from .utils import get_flat_entries, group_entries, get_xml_from_university_event_calendar

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
    
    return render(request, 'events/events_index_page.html', {
        'content_div_css': 'container body-container col-xs-12 col-lg-11 col-lg-offset-1',
        'entries': entries_out,
        'next_link': next_start.strftime('%Y-%m-%d'),
        'previous_link': previous_start.strftime('%Y-%m-%d'),
        'start': start.strftime('%Y-%m-%d'),
        'start_label': start.strftime('%B %d, %Y'),
        'stop': stop.strftime('%Y-%m-%d'),
        'view': view
    })
