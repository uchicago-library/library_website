from django.shortcuts import render
from public.models import LocationPage, LocationPageFloorPlacement
from wagtail.wagtailimages.models import Image
from public.models import StandardPage
from library_website.settings import PUBLIC_HOMEPAGE
from base.utils import get_hours_and_location, sort_buildings
from ask_a_librarian.utils import get_chat_status, get_chat_status_css, get_unit_chat_link
from public.utils import get_features, has_feature


def spaces(request):
    building = request.GET.get('building', None)
    feature = request.GET.get('feature', None)
    floor = request.GET.get('floor', None)
    space_type = request.GET.get('space_type', 'is_study_space')

    possible_features = get_features() 

    # validate form input.
    if not building in LocationPage.objects.filter(is_building=True).values_list('title', flat=True):
        building = None
    if not has_feature(feature):
        feature = None
    if not space_type in ['is_study_space', 'is_teaching_space', 'is_event_space']:
        space_type = None

    # get the feature label. 
    feature_label = ''
    if feature:
        for f in possible_features:
            if f[0] == feature:
                feature_label = f[1]

    # get spaces.
    spaces = LocationPage.objects.live()
    if building:
        spaces = spaces.filter(parent_building = LocationPage.objects.get(title=building))
    if feature:
        spaces = spaces.filter(**{feature: True})
    if floor:
        location_ids = LocationPageFloorPlacement.objects.filter(floor__title=floor).values_list('parent', flat=True)
        spaces = spaces.filter(id__in=location_ids)
    if space_type:
        spaces = spaces.filter(**{space_type: True})

    # Narrow down list of buildings from all buildings by using feature
    # and space_type, create list of libraries for display in dropdown
    # from parent_building of filtered all_buildings. Use set to remove
    # duplicates and sort_buildings to organize resulting list of libraries
    all_buildings = LocationPage.objects.all()
    if feature:
        all_buildings = all_buildings.filter(**{feature: True})
    if space_type:
        all_buildings = all_buildings.filter(**{space_type: True})
    buildings = []
    for b in all_buildings:
        buildings.append(b.parent_building)
    buildings = sort_buildings(list(set(buildings)))

    # make sure all features have at least one LocationPage for the current space_type. 
    features = list(filter(lambda f: spaces.filter(**{f[0]: True}), possible_features))

    # if a library building has been set, get floors that are appropriate for
    # the parameters that have been set. 
    floors = []
    if building:
        # Changed spaces to all_buildings in id_list to bypass filtering in spaces.
        # get all locations that are descendants of this building. 
        id_list = all_buildings.filter(parent_building__title=building).values_list('pk', flat=True)
        # get a unique, sorted list of the available floors here. 
        floors = sorted(list(set(LocationPageFloorPlacement.objects.filter(parent__in=id_list).exclude(floor=None).values_list('floor__title', flat=True))))

    default_image = Image.objects.get(title="Default Placeholder Photo")

    # Page context variables for templates
    home_page = StandardPage.objects.live().get(id=PUBLIC_HOMEPAGE)
    location_and_hours = get_hours_and_location(home_page)
    location = str(location_and_hours['page_location'])
    unit = location_and_hours['page_unit']

    return render(request, 'public/spaces_index_page.html', {
        'building': building,
        'buildings': buildings,
        'breadcrumb_div_css': 'col-md-12 breadcrumbs hidden-xs hidden-sm',
        'content_div_css': 'container body-container col-xs-12 col-lg-11 col-lg-offset-1',
        'default_image': default_image,
        'feature': feature,
        'feature_label': feature_label,
        'features': features,
        'floor': floor,
        'floors': floors,
        'self': {
            'title': 'Library Spaces'
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
    })
