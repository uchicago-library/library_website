import base64
import json
from http.client import HTTPSConnection

import requests
from django.utils.text import slugify
from library_website.settings import (
    ADDRESS_TEMPLATE, CRERAR_HOMEPAGE, DANGELO_HOMEPAGE, ECKHART_HOMEPAGE,
    HOURS_PAGE, HOURS_TEMPLATE, LIBCAL_IID, MANSUETO_HOMEPAGE, SCRC_HOMEPAGE,
    SSA_HOMEPAGE
)
from wagtail.models import Page
from wagtail.documents.models import Document

try:
    from library_website.settings.local import (
        DIRECTORY_PASSWORD, DIRECTORY_USERNAME, DIRECTORY_WEB_SERVICE
    )
except (ImportError):
    import os
    DIRECTORY_USERNAME = os.environ['DIRECTORY_USERNAME']
    DIRECTORY_WEB_SERVICE = os.environ['DIRECTORY_WEB_SERVICE']
    DIRECTORY_PASSWORD = os.environ['DIRECTORY_PASSWORD']

HOURS_UNAVAILABLE = 'Unavailable'


def get_xml_from_directory_api(url):
    assert url.startswith('https://')

    xml_path = url.replace('https://', '')
    xml_path = xml_path.replace(DIRECTORY_WEB_SERVICE, '')
    c = HTTPSConnection(DIRECTORY_WEB_SERVICE)
    b = bytes(DIRECTORY_USERNAME + ':' + DIRECTORY_PASSWORD, 'utf-8')
    userAndPass = base64.b64encode(b).decode("ascii")
    headers = {'Authorization': 'Basic %s' % userAndPass}
    c.request('GET', xml_path, headers=headers)
    result = c.getresponse()
    return result.read()


def get_json_for_library(lid):
    """
    Get json data for a specific library from
    the libcal api.

    Args:
        lid: integer, library ID in libcal.

    Returns:
        string, json
    """
    json = requests.get(
        'https://api3.libcal.com/api_hours_today.php?iid=' + str(LIBCAL_IID) +
        '&lid=' + str(lid) + '&format=json'
    ).json()

    if json:
        for item in json['locations']:
            if item['lid'] == lid:
                return item


def get_json_for_libraries(lids):
    """
    Get json data for a list of libraries from
    the libcal api.

    Args:
        lids: list of integers, library IDs in
        libcal.

    Returns:
        dict, json data
    """
    lids = ','.join([str(i) for i in lids])
    url = 'https://api3.libcal.com/api_hours_today.php?iid=' + \
        str(LIBCAL_IID) + '&lids=' + str(lids) + '&format=json'

    try:
        jdict = requests.get(url, timeout=12).json()
    except requests.exceptions.Timeout:
        jdict = json.loads(
            '{"locations":[{"lid":1373,"name":"Crerar","rendered":""},{"lid":1378,"name":"D\'Angelo Law","rendered":""},{"lid":1377,"name":"Eckhart","rendered":""},{"lid":1379,"name":"Mansueto","rendered":""},{"lid":1357,"name":"Regenstein","rendered":""},{"lid":2449,"name":"Special Collections","rendered":""},{"lid":1380,"name":"SSA","rendered":""}]}'
        )
    return jdict


def get_hours_by_id(lid):
    """
    Get today's hours for a specific library.

    Args:
        lid: integer or string, library ID in libcal.

    Returns:
        string, today's hours for location.
    """
    data = get_json_for_library(int(lid))
    msg = HOURS_UNAVAILABLE
    try:
        hours = data['rendered']
        if hours != '':
            return hours
        else:
            return msg
    except:
        return msg


def process_hours(hours):
    """
    Process the hours string for display.

    Args:
        hours: string, json array
    """
    msg = HOURS_UNAVAILABLE
    if hours != '':
        return hours
    else:
        return msg


def get_all_building_hours():
    """
    Get the hours for all buldings
    in the system.

    Returns:
        list of strings.
    """
    from public.models import LocationPage
    buildings = list(
        (str(p), p.libcal_library_id)
        for p in LocationPage.objects.live().filter(is_building=True)
        if p.libcal_library_id is not None
    )
    return list(
        HOURS_TEMPLATE % (b[0], get_hours_by_id(b[1])) for b in buildings
    )


# def get_building_hours_and_lid_DEPRECATED():
#    """
#    Get all libcal houurs for buildings along
#    with the corresponding libcal library ID.
#
#    Returns:
#        A list of tuples where the first item
#        is a libcal library ID and the second
#        item is the hours presented as a string.
#    """
#    from public.models import LocationPage
#    buildings = []
#    for page in LocationPage.objects.live().filter(is_building=True):
#        if page.libcal_library_id:
#            llid = page.libcal_library_id
#            hours = HOURS_TEMPLATE % (str(page), get_hours_by_id(llid))
#            buildings.append((str(llid), str(hours)))
#    return buildings


def get_json_hours_by_id(llid, hours):
    """
    Pull the hours for a specific id out
    of a json string with many hours.

    Args:
        llid: integer, libcal library id

        hours: string, json

    Returns:
        string, hours
    """
    for item in json.loads(hours):
        if item[0] == llid:
            return item[1]
    return HOURS_UNAVAILABLE


def get_building_hours_and_lid(current_site):
    """
    Get all libcal houurs for buildings along
    with the corresponding libcal library ID.

    Args:
        current_site: wagtail site object from
        request.

    Returns:
        A list of tuples where the first item
        is a libcal library ID the second item
        is the hours presented as a string and
        the third item is an anchor link to the
        hours and locations page.
    """
    from public.models import LocationPage
    buildings = []
    llids = []
    library_data = {}
    hours_page = Page.objects.get(id=HOURS_PAGE)
    base_url = hours_page.relative_url(current_site)
    for library in LocationPage.objects.live().filter(is_building=True):
        library_id = library.libcal_library_id
        if library.libcal_library_id:
            llids.append(library_id)
            data = {}
            libname = str(library)
            data['name'] = libname
            data['url'] = base_url + '#' + slugify(libname)
            library_data[library_id] = data

    library_hours = get_json_for_libraries(llids)
    for page in library_hours['locations']:
        llid = int(page['lid'])
        if llid in llids:
            hours = HOURS_TEMPLATE % (
                page['name'], process_hours(page['rendered'])
            )
            buildings.append((str(llid), str(hours), library_data[llid]['url']))
    return buildings


def recursive_get_parent_building(location):
    """
    Return the "highest" location level for a
    given sub-location. This should resolve
    to a building if the data is setup correctly.

    Args:
        location: location page object.

    Returns:
        location page objects
    """
    # Base case
    if location.is_building:
        return location
    # Recursive case
    else:
        return recursive_get_parent_building(location.parent_building)


def get_hours_and_location(obj):
    """
    Gets the page unit, location, hours and the address
    in one pass. We get these at the same time in order to
    minimize calls to the database and centralize the display
    logic since these all need to reach out to unit > location.

    Args:
        obj: page object (self).

    Returns:
        A mixed dictionary of objects and strings formatted for
        display in the header and footer templates. The hours
        key contains the hours from libcal. The key with
        address information contains the address information
        from the proper location content type.

        Keys:
        ----------------------------------------------------
        page_unit: the unit of the current page or a generic
        fallback from the config.

        page_location: the location to display based on unit.
        If the page's unit > location is a building e.g.
        is_building = True, then use that location, otherwise
        use unit > location > parent_building. If for some
        reason nothing is found, use Regenstein.

        hours: get the current building name and hours for
        a page. If the page's unit > location is a building e.g.
        is_building = True, then display the name and hours
        for that location, otherwise pull hours from
        unit > location > parent_building. If for some reason
        nothing is found, use the hours for Regenstein.

        address: the address entry gets the address from the
        same location used to define the libcal hours in the
        previously mentioned hours key.
        ----------------------------------------------------
    """
    # Set unit, location, and hours
    try:
        unit = obj.unit
        location = recursive_get_parent_building(unit.location)
        libcalid = location.libcal_library_id
        # hours = HOURS_TEMPLATE % (str(location), get_hours_by_id(location.libcal_library_id))
    except (AttributeError):
        from units.utils import get_default_unit
        unit = get_default_unit()
        location = fallback = unit.location
        libcalid = fallback.libcal_library_id
        # hours =  HOURS_TEMPLATE % (str(fallback), get_hours_by_id(fallback.libcal_library_id))

    # Set address
    if location.address_2:
        address = location.address_1 + ', ' + location.address_2
    else:
        address = location.address_1

    # Return everything at once
    return {
        'page_location':
        location,
        'page_unit':
        unit,
        # 'hours': hours,
        'libcalid':
        libcalid,
        'address':
        ADDRESS_TEMPLATE %
        (address, location.city, location.state, str(location.postal_code))
    }


def get_specific_page_data(idnum, key):
    """
    Helper function for getting specific data for a page
    by ID. The data returned is that from the
    get_hours_an_location data structure.

    Args:
        idnum: integer, id of the page for which to retrieve data.

        key: sring, dictionary key from get_hours_an_location.
        Acceptable values are, "page_location", "page_unit",
        "libcalid", and "address".

    Returns:
        Mixed output, objects and strings returned from the
        get_hours_and_location data structure.
    """
    return get_hours_and_location(Page.objects.live().get(id=idnum).specific
                                  )[key]


def sort_buildings(spaces):
    """
    Sort the given list of buildings so that buildings
    always appear in standard order in dropdown select
    in spaces page. Uses libcal_library_id of main library buildings.

        If not used, buildings list will be randomly organized.
    """
    from public.models import LocationPage, StandardPage

    # LocationPage Object ids
    REG, SSA, MANSUETO, CRERAR, ECKHART, DANGELO, SCRC = 1797, 1798, 1816, 2713, 2714, 3393, 2971
    new_list = []
    pages = StandardPage.objects.live()
    id_list = spaces.values_list('parent_building', flat=True)
    # If locationpage id in list of ids of parent buildings, grab StandardPage object
    if REG in id_list:
        # pages.get(id=REGENSTEIN_HOMEPAGE).unit.location)
        new_list.append(LocationPage.objects.live().get(id=REG))
    if SSA in id_list:
        new_list.append(pages.get(id=SSA_HOMEPAGE).unit.location)
    if MANSUETO in id_list:
        new_list.append(pages.get(id=MANSUETO_HOMEPAGE).unit.location)
    if CRERAR in id_list:
        new_list.append(pages.get(id=CRERAR_HOMEPAGE).unit.location)
    if ECKHART in id_list:
        new_list.append(pages.get(id=ECKHART_HOMEPAGE).unit.location)
    if DANGELO in id_list:
        new_list.append(pages.get(id=DANGELO_HOMEPAGE).unit.location)
    if SCRC in id_list:
        new_list.append(pages.get(id=SCRC_HOMEPAGE).unit.location)
    return new_list


def get_field_for_indexing(field, iterable):
    """
    Loop over an iterable and build a string out of
    field values.

    Args:
        field: sring, field name to pull.

        iterable: QuerySet

    Returns:
        string of concatonated values to be used
        for indexing.
    """
    return ' '.join(item['summary'] for item in iterable)


def get_doc_titles_for_indexing(id_field, iterable):
    """
    Get document titles in order to index them.

    Args:
        field: string, name of a field that has
        a document id.

        iterable: QuerySet

    Returns:
        Concatonated string of all document titles for document links
        in a given iterable. Used for indexing purposes.
    """
    retval = ''
    for item in iterable:
        if item[id_field]:
            title = Document.objects.get(id=item[id_field]).title
            retval += ' %s' % (title,)
    return retval


def unfold(step, initial):
    """
    Higher-order utility function; anamorphism over generators.  Don't
    be put off by the fancy name; unfold is a useful function that
    'unpacks' a single piece of data into a generator of items that
    are the result of successively running a step function on that
    initial input.

    Args:
        step: a function from any input value to a tuple containing
        that input in the 0 slot and a transformed version of that
        input in the 1 slot; when an input that can't be transformed
        anymore is passed into it, it returns False

        initial: the initial input, to be unpacked by the step
        function

    Returns:
        generator that is the result of successively applying the
        step function to the initial input
    """

    def generator(tup):
        while True:
            tup = step(tup[1])
            if tup is False:
                break
            else:
                yield tup[0]

    return [item for item in generator((None, initial))]

gensym_ref = 0

def gensym():
    global gensym_ref
    output = "A%d" % gensym_ref
    gensym_ref +=1
    return output
