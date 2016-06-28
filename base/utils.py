import base64
from http.client import HTTPSConnection
from library_website.settings.local import DIRECTORY_WEB_SERVICE, DIRECTORY_USERNAME, DIRECTORY_PASSWORD
import requests
from library_website.settings.base import LIBCAL_IID, HOURS_TEMPLATE, ADDRESS_TEMPLATE, NEWS_CATEGORIES
import feedparser
from django.utils.html import strip_tags
from django.utils.text import slugify
from bs4 import BeautifulSoup

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


def get_events(url):
    """
    Get the workshops and events feed from Tiny Tiny RSS
    reorder the events by date and retun data formatted 
    for a restful service.

    Args:
        url: string, feed url.

    Returns:
        A list of tuples where the first item in the tuple
        is a title, the second item in the tuple is a url,
        the third item in the tuple is a date string,
        and the fourth item is a time string.
    """
    d = feedparser.parse(url)
    entries = []
    for e in d.entries:
        content = e.content[0]['value']
        # TODO: turn this into a regex
        tmp_lst = content.split('<strong>Date:</strong>')
        tmp_lst = tmp_lst[1].split('<strong>Time:</strong>')
        tmp_lst = [tmp_lst[0]] + tmp_lst[1].split('<br>')
        ds = strip_tags(tmp_lst[0]).strip()
        ts = strip_tags(tmp_lst[1]).strip()
        #dt_obj = parser.parse(ds)
        #print(dt_obj)
        title = e.title.split(': ')[1]
        entries.append((title, e.link, ds, ts))
    return entries


def display_news(tags, is_home):
    """
    Helper method for determining if a news story
    should be displayed.

    Args:
        tags: list of dictionaries, "tags: from a 
        feedparser object.

    Returns:
        Boolean
    """
    kiosk = 'library kiosk' if is_home else 'kiosk'
    flag = False
    for tag in tags:
        if tag['term'].lower() == kiosk:
            flag = True
            break
    return flag


def get_news(url, is_home):
    """
    Get news stories from a Wordpress feed and create
    a datastructure to hand off to a restful sevice.

    Args:
        url: string, link to a wordpress feed.

        is_home: boolean, is the page the Library home 
        page.

    Returns:
        A list of tuples representing a news story.
    """
    d = feedparser.parse(url)
    stories = []
    i = 4
    garbage = ['Continue&#160;reading&#160;&#187;', 'Continue&nbsp;reading&nbsp;&raquo;']
    for e in d.entries:
        if i < 1:
            break
        display = display_news(e.tags, is_home)
        for tag in e.tags:
            # Categories and tags
            cat = tag['term']
            
            # Images
            soup = BeautifulSoup(e.description, 'html.parser')
            img = soup.findAll('img')
            try:
                img_src = img[0]['src']
            except:
                img_src = ''
            if cat in NEWS_CATEGORIES and display and img_src:
                description = strip_tags(e.description).strip(garbage[0]).strip(garbage[1]) 
                stories.append((e.title, e.link, cat, description, slugify(cat), img_src))
                i -= 1
                break
    return stories


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
        lid: integer or string, library ID in libcal.

    Returns:
        string, today's hours for location.
    """
    data = get_json_for_library(int(lid))
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


def get_building_hours_and_lid():
    """
    Get all libcal houurs for buildings along 
    with the corresponding libcal library ID.

    Returns:
        A list of tuples where the first item
        is a libcal library ID and the second
        item is the hours presented as a string.
    """
    from public.models import LocationPage
    buildings = []
    for page in LocationPage.objects.live().filter(is_building=True):
        if page.libcal_library_id:
            llid = page.libcal_library_id
            hours = HOURS_TEMPLATE % (str(page), get_hours_by_id(llid))
            buildings.append((str(llid), str(hours)))
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
        #hours = HOURS_TEMPLATE % (str(location), get_hours_by_id(location.libcal_library_id))
    except(AttributeError):
        from units.utils import get_default_unit
        unit = get_default_unit()
        location = fallback = unit.location
        libcalid = fallback.libcal_library_id
        #hours =  HOURS_TEMPLATE % (str(fallback), get_hours_by_id(fallback.libcal_library_id))

    # Set address
    if location.address_2:
        address = location.address_1 + ', ' + location.address_2
    else:
        address = location.address_1

    # Return everything at once
    return {'page_location': location,
            'page_unit' : unit, 
            #'hours': hours, 
            'libcalid': libcalid,
            'address': ADDRESS_TEMPLATE % (address, location.city, location.state, str(location.postal_code)) }


