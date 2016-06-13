from django.shortcuts import render
from public.models import LocationPage

def spaces(request):
    building = request.GET.get('building', None)
    feature = request.GET.get('feature', None)
    space_type = request.GET.get('space_type', 'is_study_space')

    possible_features = [
        {'field': 'is_quiet_zone',         'label': 'Quiet Zone'},
        {'field': 'is_collaboration_zone', 'label': 'Collaboration Zone'},
        {'field': 'is_phone_zone',         'label': 'Cell Phone Zone'},
        {'field': 'is_meal_zone',          'label': 'Meal Zone'},
        {'field': 'is_open_space',         'label': 'Open Space'},
        {'field': 'is_snacks_allowed',     'label': 'Snacks Allowed'},
        {'field': 'is_24_hours',           'label': 'All Night Study'},
        {'field': 'has_printing',          'label': 'Copy / Print / Scan'},
        {'field': 'has_public_computer',   'label': 'Public Computer(s)'},
        {'field': 'has_dual_monitors',     'label': 'Dual Monitor stations'},
        {'field': 'has_book_scanner',      'label': 'Overhead Book Scanner'},
        {'field': 'has_single_tables',     'label': 'Individual Tables'},
        {'field': 'has_large_tables',      'label': 'Large Tables'},
        {'field': 'has_carrels',           'label': 'Carrels'},
        {'field': 'has_standing_desk',     'label': 'Standing Desks'},
        {'field': 'has_soft_seating',      'label': 'Comfy Seating'},
        {'field': 'is_reservable',         'label': 'Reservable'},
        {'field': 'has_board',             'label': 'Whiteboard'}
    ]

    # validate form input.
    if not building in LocationPage.objects.filter(is_building=True).values_list('title', flat=True):
        building = None
    if not feature in list(map(lambda f: f['field'], possible_features)):
        feature = None
    if not space_type in ['is_study_space', 'is_teaching_space', 'is_event_space']:
        space_type = None

    # make sure some other 
    buildings = LocationPage.objects.filter(is_building = True)


    # get the feature label. 
    feature_label = ''
    if feature:
        for f in possible_features:
            if f['field'] == feature:
                feature_label = f['label']

    # get spaces.
    spaces = LocationPage.objects.live()
    if building:
        spaces = spaces.filter(parent_building = LocationPage.objects.get(title=building))
    if feature:
        spaces = spaces.filter(**{feature: True})
    if space_type:
        spaces = spaces.filter(**{space_type: True})

    # make sure all features have at least one LocationPage for the current space_type. 
    features = list(filter(lambda f: spaces.filter(**{f['field']: True}), possible_features))

    # need a pager. 

    return render(request, 'public/spaces_index_page.html', {
        'building': building,
        'buildings': buildings,
        'content_div_css': 'container body-container col-xs-12 col-lg-11 col-lg-offset-1',
        'feature': feature,
        'feature_label': feature_label,
        'features': features,
        'self': {
            'title': 'Our Spaces'
        },
        'spaces': spaces,
        'space_type': space_type
    })
