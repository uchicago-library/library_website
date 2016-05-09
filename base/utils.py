import base64
from http.client import HTTPSConnection
from library_website.settings.local import DIRECTORY_WEB_SERVICE, DIRECTORY_USERNAME, DIRECTORY_PASSWORD
import requests
from library_website.settings.base import LIBCAL_IID, HOURS_TEMPLATE, ADDRESS_TEMPLATE

def get_xml_from_directory_api(url):
    assert url.startswith('https://')

    xml_path = url.replace('https://', '')
    xml_path = xml_path.replace(DIRECTORY_WEB_SERVICE, '')
    c = HTTPSConnection(DIRECTORY_WEB_SERVICE)
    b = bytes(DIRECTORY_USERNAME + ':' + DIRECTORY_PASSWORD, 'utf-8')
    userAndPass = base64.b64encode(b).decode("ascii")
    headers = { 'Authorization' : 'Basic %s' %  userAndPass } 
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
    url = 'https://api3.libcal.com/api_hours_today.php?iid=' + \
        str(LIBCAL_IID) + '&lid=' + str(lid) + '&format=json'

    json = requests.get('https://api3.libcal.com/api_hours_today.php?iid=' + \
        str(LIBCAL_IID) + '&lid=' + str(lid) + '&format=json').json()

    for item in json['locations']:
        if item['lid'] == lid:
            return item


def get_hours_by_id(lid):
    """
    Get today's hours for a specific library.

    Args:
        lid: integer, library ID in libcal.

    Returns:
        string, today's hours for location.
    """
    data = get_json_for_library(lid)
    msg = 'Hours Unavailable'
    try:
        hours = data['rendered']
        if hours != '': 
            return hours
        else:
            return msg
    except:
        return msg


def get_all_building_hours():
    """
    Get the hours for all buldings
    in the system.

    Returns:
        list of strings.
    """
    from public.models import LocationPage
    buildings = list((str(p), p.libcal_library_id) for p in LocationPage.objects.live().filter(is_building=True) if p.libcal_library_id != None)
    return list(HOURS_TEMPLATE % (b[0], get_hours_by_id(b[1])) for b in buildings)


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
        location = unit.location
        if location.is_building:
            location = location # Readability
            hours = HOURS_TEMPLATE % (str(location), get_hours_by_id(location.libcal_library_id))
        else:
            location = location.parent_building
            hours = HOURS_TEMPLATE % (str(location.parent_building), get_hours_by_id(location.parent_building.libcal_library_id))
    except(AttributeError):
        from units.utils import get_default_unit
        unit = get_default_unit()
        location = fallback = unit.location
        hours =  HOURS_TEMPLATE % (str(fallback), get_hours_by_id(fallback.libcal_library_id))

    # Set address
    if location.address_2:
        address = location.address_1 + ', ' + location.address_2
    else:
        address = location.address_1

    # Return everything at once
    return {'page_location': location,
            'page_unit' : unit, 
            'hours': hours, 
            'address': ADDRESS_TEMPLATE % (address, location.city, location.state, str(location.postal_code)) }


