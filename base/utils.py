import base64
from http.client import HTTPSConnection
from library_website.settings.local import DIRECTORY_WEB_SERVICE, DIRECTORY_USERNAME, DIRECTORY_PASSWORD
import requests
from library_website.settings.base import LIBCAL_IID
from defusedxml.ElementTree import fromstring

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


def get_chat_status(name):
    """
    Get the chat status for a location 
    by name. 

    Args:
        name: string, the name of the 
        chat widget you wish to retrieve.
        Possible values include: uofc-ask,
        law, crerar, and ssa.

    Returns:
        boolean
    """
    xml = requests.get('https://us.libraryh3lp.com/presence/jid/' \
        + name + '/chat.libraryh3lp.com/xml')
    tree = fromstring(xml.content)
    return tree.find('resource').attrib['show'] == 'available'

