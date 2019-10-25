import requests


FEATURES_LIST = [
    (
        'is_quiet_zone', 'Quiet Zone',
        '<i class="fa fa-bell-slash-o" aria-hidden="true"></i>'
    ),
    (
        'is_collaboration_zone', 'Collaboration Zone / Group study',
        '<i class="material-icons" aria-hidden="true">people</i>'
    ),
    (
        'is_phone_zone', 'Cell Phone Zone',
        '<i class="material-icons" aria-hidden="true">phone_android</i>'
    ),
    (
        'is_meal_zone', 'Meal Zone',
        '<i class="material-icons" aria-hidden="true">local_dining</i>'
    ),
    (
        'is_open_space', 'Open Space',
        '<i class="material-icons" aria-hidden="true">all_inclusive</i>'
    ),
    (
        'is_snacks_allowed', 'Snacks allowed',
        '<i class="material-icons" aria-hidden="true">local_cafe</i>'
    ),
    (
        'is_24_hours', 'All Night Study',
        '<i class="material-icons" aria-hidden="true">access_alarm</i>'
    ),
    (
        'has_printing', 'Copy / Print / Scan',
        '<i class="fa fa-print" aria-hidden="true"></i>'
    ),
    (
        'has_public_computer', 'Public Computer(s)',
        '<i class="fa fa-desktop" aria-hidden="true"></i>'
    ),
    (
        'has_dual_monitors', 'Dual Monitor stations',
        '<i class="material-icons" aria-hidden="true">add_to_queue</i>'
    ),
    (
        'has_book_scanner', 'Overhead Book Scanner',
        '<i class="material-icons" aria-hidden="true">import_contacts</i>'
    ),
    (
        'has_screen', 'Monitor/Projector',
        '<i class="material-icons" aria-hidden="true">cast</i>'
    ),
    (
        'has_single_tables', 'Individual Tables',
        '<i class="material-icons" aria-hidden="true">widgets</i>'
    ),
    (
        'has_large_tables', 'Large Tables',
        '<i class="material-icons" aria-hidden="true">wb_iridescent</i>'
    ),
    (
        'has_carrels', 'Carrels',
        '<i class="material-icons" aria-hidden="true">border_inner</i>'
    ),
    (
        'has_standing_desk', 'Standing Desks',
        '<i class="material-icons" aria-hidden="true">accessibility</i>'
    ),
    (
        'has_soft_seating', 'Comfy Seating',
        '<i class="material-icons" aria-hidden="true">weekend</i>'
    ),
    (
        'has_board', 'White Board',
        '<i class="material-icons" aria-hidden="true">gesture</i>'
    ),
    (
        'is_reservable', 'Reservable',
        '<i class="fa fa-calendar-plus-o" aria-hidden="true"></i>'
    ),
    (
        'is_no_food_allowed', 'No Food',
        '<i class="fa fa-ban" aria-hidden="true"></i>'
    ),
    (
        'has_lockers', 'Lockers',
        '<i class="material-icons" aria-hidden="true">lock_open</i>'
    ),
    (
        'has_day_lockers', 'Day Lockers',
        '<i class="material-icons" aria-hidden="true">lock_open</i>'
    ),
]


# helper functions for /switchboard route


def get_features():
    """
    Boolean fields we use as "features" in the
    spaces browse and page display.

    Returns:
        List of tuples containing three strings where
        the first item is a field name, the second item
        is a display label and the third item is an
        html icon for display.
    """
    return FEATURES_LIST


def has_feature(feature):
    """
    See if a given feature is in the features list

    Args:
        feature: string, field name to search for.

    Returns:
        Boolean
    """
    for item in get_features():
        if item[0] == feature:
            return True
    return False


def full_mk_url(bare_url, doi):
    '''
    given DOI and URL for idresolve service, output query url for SFX
    callback is called 'redundant' because this code isn't using it

    '''
    output = (
        f'{bare_url}'
        '?code=9344'
        '&function=idresolve'
        '&callback=redundant'
        f'&id={doi}'
        )
    return output


def mk_url(doi):
    '''
    given just DOI, output query url for SFX

    '''
    # this is for local testing; for production, change bare_url to
    # https://lib.uchicago.edu/cgi-bin/idresolve
    bare_url = "http://sequent.lib.uchicago.edu:8081"
    return full_mk_url(bare_url, doi)


def doi_lookup(doi):
    '''
    query the DOI resolver service, return SFX URL if DOI is valid,
    otherwise return None

    '''
    url = mk_url(doi)
    response = requests.get(url)
    if response.status_code % 400 < 100:
        return None
    else:
        return response.text


def get_clean_params(request):
    '''
    return parameters that have been passed to a POST request,
    omitting the CSRF token

    '''
    params = request.POST
    clean_params = dict(
        filter(
            lambda x: x[0] != 'csrfmiddlewaretoken',
            params.items()
        )
    )
    return clean_params


def get_first_param(request):
    '''
    given a request, return the value of the first query string
    parameter, whatever the key happens to be called

    '''
    params = get_clean_params(request)
    if params:
        first_key = list(params.keys())[0]
        first_value = params[first_key]
        return first_value
    else:
        return None
