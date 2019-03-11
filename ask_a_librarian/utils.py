import requests
from defusedxml.ElementTree import fromstring
from wagtail.core.models import Site

from library_website.settings import (
    DEFAULT_UNIT, SCRC_ASK_PAGE, SCRC_MAIN_UNIT
)


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

    try:
        xml = requests.get(
            'https://us.libraryh3lp.com/presence/jid/' + name +
            '/chat.libraryh3lp.com/xml',
            timeout=12
        )
        tree = fromstring(xml.content)
    except requests.exceptions.Timeout:
        xml = "<presence user='" + name + \
            "' server='chat.libraryh3lp.com'><resource show='unavailable' name='libraryh3lp' priority='5'/></presence>"
        tree = fromstring(xml)

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


def get_chat_status_and_css(name):
    """
    Get the chat status and css for Ask a
    Librarian pages.

    Args:
        name: string, the name of the chat
        widget you wish to retrieve. Possible
        values include: uofc-ask, law, crerar,
        and ssa.

    Returns:
        Tuple representing the chat status for
        Ask a Librarian pages where the first
        item is a boolean and the second item
        is a string (css class).
    """

    try:
        xml = requests.get(
            'https://us.libraryh3lp.com/presence/jid/' + name +
            '/chat.libraryh3lp.com/xml',
            timeout=12
        )
        tree = fromstring(xml.content)
    except requests.exceptions.Timeout:
        xml = "<presence user='" + name + \
            "' server='chat.libraryh3lp.com'><resource show='unavailable' name='libraryh3lp' priority='5'/></presence>"
        tree = fromstring(xml)
    status_lookup = {True: 'active', False: 'off'}
    status_bool = tree.find('resource').attrib['show'] == 'available'
    return (status_bool, status_lookup[status_bool])


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
    return {
        'uofc-ask': get_chat_status_css('uofc-ask'),
        'crerar': get_chat_status_css('crerar'),
        'eckhart': get_chat_status_css('crerar'),
        'law': get_chat_status_css('law'),
        'ssa': get_chat_status_css('ssa'),
        'dissertation-office': get_chat_status_css('dissertation-office')
    }


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
    from wagtail.core.models import Page
    current_site = Site.find_for_request(request)

    try:
        if unit.id == SCRC_MAIN_UNIT:
            return Page.objects.live().get(id=SCRC_ASK_PAGE).relative_url(current_site)
        return AskPage.objects.live().get(unit=unit).relative_url(current_site)
    except:
        return AskPage.objects.live().get(unit=DEFAULT_UNIT).relative_url(current_site)
