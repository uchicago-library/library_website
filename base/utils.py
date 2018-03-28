import base64
from http.client import HTTPSConnection
try:
    from library_website.settings.local import DIRECTORY_WEB_SERVICE, DIRECTORY_USERNAME, DIRECTORY_PASSWORD
except(ImportError):
    import os
    DIRECTORY_USERNAME = os.environ['DIRECTORY_USERNAME']
    DIRECTORY_WEB_SERVICE = os.environ['DIRECTORY_WEB_SERVICE']
    DIRECTORY_PASSWORD = os.environ['DIRECTORY_PASSWORD']

import requests
from library_website.settings import LIBCAL_IID, HOURS_TEMPLATE, ADDRESS_TEMPLATE, NEWS_CATEGORIES, HOURS_PAGE
import feedparser
from django.utils.html import strip_tags
from django.utils.text import slugify
from bs4 import BeautifulSoup
import json
from wagtail.core.models import Page
from library_website.settings import REGENSTEIN_HOMEPAGE, SSA_HOMEPAGE, MANSUETO_HOMEPAGE, CRERAR_HOMEPAGE, ECKHART_HOMEPAGE, DANGELO_HOMEPAGE, SCRC_HOMEPAGE

HOURS_UNAVAILABLE = 'Unavailable'

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


def get_news(url):
    """
    Get news stories from a Wordpress feed and create
    a datastructure to hand off to a restful sevice.

    Args:
        url: string, link to a wordpress feed.

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
            if cat in NEWS_CATEGORIES and img_src:
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
        jdict = json.loads('{"locations":[{"lid":1373,"name":"Crerar","rendered":""},{"lid":1378,"name":"D\'Angelo Law","rendered":""},{"lid":1377,"name":"Eckhart","rendered":""},{"lid":1379,"name":"Mansueto","rendered":""},{"lid":1357,"name":"Regenstein","rendered":""},{"lid":2449,"name":"Special Collections","rendered":""},{"lid":1380,"name":"SSA","rendered":""}]}')
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
    buildings = list((str(p), p.libcal_library_id) for p in LocationPage.objects.live().filter(is_building=True) if p.libcal_library_id != None)
    return list(HOURS_TEMPLATE % (b[0], get_hours_by_id(b[1])) for b in buildings)


#def get_building_hours_and_lid_DEPRECATED():
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
            hours = HOURS_TEMPLATE % (page['name'], process_hours(page['rendered']))
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
    return get_hours_and_location(Page.objects.live().get(id=idnum).specific)[key]


def get_page_loc_name(idnum):
    """
    Get the name of a page_location for a specific library page.

    Args:
        idnum: integer, id of the page for which to retrieve data.

    Returns:
        string, the name of the parent location under which 
        a page resides.
    """
    return str(get_specific_page_data(idnum, 'page_location'))


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
    id_list = spaces.values_list('parent_building',flat=True)
	#If locationpage id in list of ids of parent buildings, grab StandardPage object
    if REG in id_list:
        new_list.append(LocationPage.objects.live().get(id=REG))#pages.get(id=REGENSTEIN_HOMEPAGE).unit.location)
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
