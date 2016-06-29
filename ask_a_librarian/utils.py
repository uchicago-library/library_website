import requests
from defusedxml.ElementTree import fromstring
from wagtail.wagtailcore.models import Site
from library_website.settings import DEFAULT_UNIT

def get_chat_status(name):
    """
    Get the chat status for a location by name. 

    Args:
        name: string, the name of the chat widget 
        you wish to retrieve. Possible values 
        include: uofc-ask, law, crerar, and ssa.

    Returns:
        boolean
    """
    xml = requests.get('https://us.libraryh3lp.com/presence/jid/' \
        + name + '/chat.libraryh3lp.com/xml')
    tree = fromstring(xml.content)
    return tree.find('resource').attrib['show'] == 'available'


def get_chat_status_css(name):
    """
    Get the current css class name for a given
    Ask a Librarian chat widget status.

    Args:
        name: string, the name of the chat widget 
        you wish to retrieve. Possible values 
        include: uofc-ask, law, crerar, and ssa.

    Returns:
        string, css class. 
    """
    status = {True: 'active', False: 'off'}
    return status[get_chat_status(name)]


def get_chat_statuses():
    """
    Get a dictionary of chat statuses for all
    of the Ask a Librarian chat widgets. Statuses
    are represented as css classnames to be
    applied in the templates.

    Returns:
        dictionary of css classes for all of 
        the Ask a Librarian chat widgets.
    """
    return {'uofc-ask': get_chat_status_css('uofc-ask'), 
            'crerar': get_chat_status_css('crerar'),
            'law': get_chat_status_css('law'),
            'ssa': get_chat_status_css('ssa')}


def get_unit_chat_link(unit, request):
    """
    Get a link to the Ask a Librarian page
    that corresponds to a given UnitPage.

    Args:
        unit: page object.

        request: object

    Returns:
        string, url. Returns an empty string 
        upon failure.
    """
    from .models import AskPage

    try:
        return AskPage.objects.live().get(unit=unit).url
    except:
        return AskPage.objects.live().get(unit=DEFAULT_UNIT).url
