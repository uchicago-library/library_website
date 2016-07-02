from django.shortcuts import render
from django.http import JsonResponse
import json
from base.utils import get_all_building_hours, get_hours_and_location, get_json_hours_by_id, get_building_hours_and_lid, get_events, get_news
from units.utils import get_default_unit
import urllib

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
            all_building_hours = json.dumps(get_building_hours_and_lid())
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
        feed = request.GET['feed']
        return JsonResponse(
            {
                'events': get_events(feed),
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
