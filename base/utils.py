import base64
from http.client import HTTPSConnection
from library_website.settings.local import DIRECTORY_WEB_SERVICE, DIRECTORY_USERNAME, DIRECTORY_PASSWORD
import requests
from library_website.settings.base import LIBCAL_IID, HOURS_TEMPLATE

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
    try:
        return data['rendered']
    except:
        return ''


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
