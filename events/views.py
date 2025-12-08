import calendar
import datetime

from django.shortcuts import render
from wagtail.models import Site

from alerts.utils import get_browse_alerts
from ask_a_librarian.utils import (
    get_chat_status,
    get_chat_status_css,
    get_unit_chat_link,
)
from base.utils import get_hours_and_location
from library_website.settings import PUBLIC_HOMEPAGE, TTRSS_FEED, UC_EVENTS_FEED
from public.models import StandardPage

from .utils import get_events


def events(request):
    start_str = request.GET.get("start", None)
    if start_str:
        start = datetime.datetime.strptime(start_str, "%Y-%m-%d").date()
    else:
        start = datetime.date.today()
        start_str = start.strftime("%Y-%m-%d")

    # if the date was in the past, set it to today.
    if start < datetime.datetime.now().date():
        start = datetime.datetime.now().date()
        start_str = start.strftime("%Y-%m-%d")

    # get start and stop dates, along with previous start and next start dates.
    number_of_days_this_month = calendar.monthrange(start.year, start.month)[1]
    stop = start + datetime.timedelta(days=number_of_days_this_month - 1)
    stop_str = stop.strftime("%Y-%m-%d")

    if start.month == 1:
        number_of_days_last_month = calendar.monthrange(start.year - 1, 12)[1]
    else:
        number_of_days_last_month = calendar.monthrange(start.year, start.month - 1)[1]
    previous_start = start - datetime.timedelta(days=number_of_days_last_month)
    next_start = stop + datetime.timedelta(days=1)

    entries = get_events(UC_EVENTS_FEED, TTRSS_FEED, start, stop)

    # remove multiday events.
    d = len(entries) - 1
    while d >= 0:
        e = len(entries[d][1]) - 1
        while e >= 0:
            end_date = entries[d][1][e]["end_date"]
            if entries[d][1][e]["start_date"] != end_date and end_date != "":
                del entries[d][1][e]
                if not entries[d][1]:
                    del entries[d]
            e = e - 1
        d = d - 1

    # separate multiday events out into their own section.
    # multiday_events aren't arranged into something with start dates.
    tmp = get_events(UC_EVENTS_FEED, TTRSS_FEED, None, None)
    multiday_entries = []
    for event_list in [ev[1] for ev in tmp]:
        for e in event_list:
            if e["start_date"] != e["end_date"]:
                if (
                    e["sortable_date"] <= stop_str
                    and e["sortable_end_date"] >= start_str
                ):
                    multiday_entries.append(e)

    # Page context variables for templates
    home_page = StandardPage.objects.live().get(id=PUBLIC_HOMEPAGE)
    location_and_hours = get_hours_and_location(home_page)
    location = str(location_and_hours["page_location"])
    unit = location_and_hours["page_unit"]
    current_site = Site.find_for_request(request)
    alert_data = get_browse_alerts(current_site)

    next_link = next_start.strftime("%Y-%m-%d")
    previous_link = previous_start.strftime("%Y-%m-%d")

    # don't allow browsing into the past.
    if start == datetime.datetime.now().date():
        previous_link = ""

    return render(
        request,
        "events/events_index_page.html",
        {
            "breadcrumb_div_css": "col-md-12 breadcrumbs hidden-xs hidden-sm",
            "content_div_css": "container body-container col-xs-12 col-lg-11 col-lg-offset-1",
            "entries": entries,
            "multiday_entries": multiday_entries,
            "next_link": next_link,
            "previous_link": previous_link,
            "start": start.strftime("%Y-%m-%d"),
            "start_label": start.strftime("%B %d, %Y").replace(" 0", " "),
            "stop": stop.strftime("%Y-%m-%d"),
            "stop_label": stop.strftime("%B %d, %Y").replace(" 0", " "),
            "page_unit": str(unit),
            "page_location": location,
            "address": location_and_hours["address"],
            "chat_url": get_unit_chat_link(unit, request),
            "chat_status": get_chat_status("uofc-ask"),
            "chat_status_css": get_chat_status_css("uofc-ask"),
            "hours_page_url": home_page.get_hours_page(request),
            "self": {"title": "Library Events"},
            "has_alert": alert_data[0],
            "alert_message": alert_data[1][0],
            "alert_level": alert_data[1][1],
            "alert_more_info": alert_data[1][2],
            "alert_link": alert_data[1][3],
        },
    )
