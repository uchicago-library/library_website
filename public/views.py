from urllib import parse

import re

from django.http import HttpResponse
from django.shortcuts import redirect, render

import simplejson
from alerts.utils import get_browse_alerts
from ask_a_librarian.utils import (
    get_chat_status, get_chat_status_css, get_unit_chat_link
)
from base.models import UNFRIENDLY_ARTICLES
from base.utils import get_hours_and_location, sort_buildings
from library_website.settings import (
    CRERAR_HOMEPAGE, DANGELO_HOMEPAGE, ECKHART_HOMEPAGE, MANSUETO_HOMEPAGE,
    PUBLIC_HOMEPAGE, SCRC_HOMEPAGE, SSA_HOMEPAGE
)
from public.models import (
    LocationPage, LocationPageFloorPlacement, StandardPage
)
from public.utils import (
    doi_lookup, get_clean_params, get_features, get_first_param, has_feature,
    switchboard_url
)
from wagtail.core.models import Site
from wagtail.images.models import Image
from wagtailcache.cache import cache_page


def navigation(request):
    callback = request.GET.get('callback', None)

    # set up some variables to render things on the page.
    home_page = StandardPage.objects.live().get(id=PUBLIC_HOMEPAGE)
    location_and_hours = get_hours_and_location(home_page)
    llid = home_page.get_granular_libcal_lid(home_page.unit)
    location = str(location_and_hours['page_location'])
    unit = location_and_hours['page_unit']

    # html_str is not serializable...what is this thing?
    html_str = render(
        request, 'public/standard_page.html', {
            'address': location_and_hours['address'],
            'chat_url': get_unit_chat_link(unit, request),
            'hours_page_url': home_page.get_hours_page(request),
            'libcalid': llid,
            'page_location': location,
        }
    ).content

    data = '%s(%s);' % (callback, simplejson.dumps(html_str))
    return HttpResponse(data, 'text/javascript')


def switchboard(request):
    """
    route that intercepts a search query, forwards it to the DOI
    resolver if it's a DOI, and otherwise forwards the query to its
    normal destination

    note: this code assumes that the first parameter posted by the
    search box is the search term

    Args: 
        a POST request

    Returns:
        a redirect either to Find It! or to the /switchboard route
    """
    search_term = get_first_param(request)
    params = get_clean_params(request)
    doi_url = doi_lookup(search_term)

    browse_options = ['browse_title', 'browse_journal', 'browse_lcc']

    def trim(str):
        if re.match(r'browse_(.*)', str) is not None:
            return re.match(r'browse_(.*)', str)[1]
        else:
            return str

    if doi_url:
        # case where user entered a DOI
        return redirect(doi_url)
    else:
        # otherwise: pass query string along to wherever it was going
        form = params['which-form']
        p_type = params['type']
        if form == 'articles':
            # add a 'bquery' parameter to make the ebscohost API happy
            params['bquery'] = search_term
        elif form == 'catalog' and p_type in browse_options:
            params['from'] = params['lookfor']
            del params['lookfor']
            params['source'] = trim(p_type)
            del params['type']
        else:
            pass

        try:
            formtype = p_type
        except KeyError:
            formtype = ''

        url_prefix = switchboard_url(form, form_option=formtype)
        del params['which-form']
        query_string = parse.urlencode(params)
        url = f'{url_prefix}?{query_string}'
        return redirect(url)


@cache_page
def spaces(request):
    building = request.GET.get('building', None)
    feature = request.GET.get('feature', None)
    floor = request.GET.get('floor', None)
    space_type = request.GET.get('space_type', 'is_study_space')

    possible_features = get_features()

    # validate form input.
    loc_pages = LocationPage.objects.filter(is_building=True
                                            ).values_list('title', flat=True)
    if building not in loc_pages:
        building = None
    if not has_feature(feature):
        feature = None
    if space_type not in [
        'is_study_space', 'is_teaching_space', 'is_event_space',
        'is_special_use'
    ]:
        space_type = None

    # get the feature label.
    feature_label = ''
    if feature:
        for f in possible_features:
            if f[0] == feature:
                feature_label = f[1]

    # get spaces.
    spaces = LocationPage.objects.live().order_by('title').select_related(
        'parent_building', 'location_photo'
    )
    if building:
        spaces = spaces.filter(
            parent_building=LocationPage.objects.get(title=building)
        )
    if feature:
        spaces = spaces.filter(**{feature: True})
    if floor:
        location_ids = LocationPageFloorPlacement.objects.filter(
            floor__title=floor
        ).values_list('parent', flat=True)
        spaces = spaces.filter(id__in=location_ids)
    if space_type:
        spaces = spaces.filter(**{space_type: True})

    # Narrow down list of buildings from all buildings by using feature
    # and space_type, create list of libraries for display in dropdown
    # from parent_building of filtered all_spaces. Use set to remove
    # duplicates and sort_buildings to organize resulting list of libraries
    all_spaces = LocationPage.objects.live()
    if feature:
        all_spaces = all_spaces.filter(**{feature: True})
    if space_type:
        all_spaces = all_spaces.filter(**{space_type: True})
    buildings = sort_buildings(all_spaces)

    # make sure all features have at least one LocationPage for the current space_type.
    features = list(
        filter(lambda f: spaces.filter(**{f[0]: True}), possible_features)
    )

    # if a library building has been set, get floors that are appropriate for
    # the parameters that have been set.
    floors = []
    if building:
        # Changed spaces to all_spaces in id_list to bypass filtering in spaces.
        # get all locations that are descendants of this building.
        id_list = all_spaces.filter(parent_building__title=building
                                    ).values_list('pk', flat=True)
        # get a unique, sorted list of the available floors here.
        floors = sorted(
            list(
                set(
                    LocationPageFloorPlacement.objects.filter(
                        parent__in=id_list
                    ).exclude(floor=None
                              ).values_list('floor__title', flat=True)
                )
            )
        )

    default_image = Image.objects.get(title="Default Placeholder Photo")
    # If building is selected pass respective page id to page context variables,
    # else pass PUBLIC_HOMEPAGE, llid passed to render correct hours in js script,
    PAGE_ID = PUBLIC_HOMEPAGE
    if building:
        if building == 'Social Service Administration Library':
            PAGE_ID = SSA_HOMEPAGE
        elif building == 'The Joe and Rika Mansueto Library':
            PAGE_ID = MANSUETO_HOMEPAGE
        elif building == 'The John Crerar Library':
            PAGE_ID = CRERAR_HOMEPAGE
        elif building == 'Eckhart Library':
            PAGE_ID = ECKHART_HOMEPAGE
        elif building == 'The D\'Angelo Law Library':
            PAGE_ID = DANGELO_HOMEPAGE
        elif building == 'Special Collections Research Center':
            PAGE_ID = SCRC_HOMEPAGE

    # Page context variables for templates
    home_page = StandardPage.objects.live().get(id=PAGE_ID)
    friendly_name = home_page.friendly_name
    llid = home_page.get_granular_libcal_lid(home_page.unit)
    location_and_hours = get_hours_and_location(home_page)
    location = str(location_and_hours['page_location'])
    unit = location_and_hours['page_unit']
    current_site = Site.find_for_request(request)
    alert_data = get_browse_alerts(current_site)
    unfriendly_a = True if friendly_name.strip(
    ) in UNFRIENDLY_ARTICLES else False

    # Find banner for given home_page and add to context
    section_info = home_page.get_banner(current_site)
    return render(
        request, 'public/spaces_index_page.html', {
            'building': building,
            'buildings': buildings,
            'breadcrumb_div_css': 'col-md-12 breadcrumbs hidden-xs hidden-sm',
            'content_div_css':
            'container body-container col-xs-12 col-lg-11 col-lg-offset-1',
            'default_image': default_image,
            'feature': feature,
            'feature_label': feature_label,
            'features': features,
            'floor': floor,
            'floors': floors,
            'self': {
                'title': 'Library Spaces',
                'friendly_name': friendly_name
            },
            'spaces': spaces,
            'space_type': space_type,
            'page_unit': str(unit),
            'page_location': location,
            'address': location_and_hours['address'],
            'chat_url': get_unit_chat_link(unit, request),
            'chat_status': get_chat_status('uofc-ask'),
            'chat_status_css': get_chat_status_css('uofc-ask'),
            'hours_page_url': home_page.get_hours_page(request),
            'unfriendly_a': unfriendly_a,
            'libcalid': llid,
            'has_banner': section_info[0],
            'banner': section_info[1],
            'banner_feature': section_info[2],
            'banner_title': section_info[3],
            'banner_subtitle': section_info[4],
            'banner_url': section_info[5],
            'branch_lib_css': home_page.get_branch_lib_css_class(),
            'has_alert': alert_data[0],
            'alert_message': alert_data[1][0],
            'alert_level': alert_data[1][1],
            'alert_more_info': alert_data[1][2],
            'alert_link': alert_data[1][3],
        }
    )
