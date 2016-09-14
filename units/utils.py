from library_website.settings import DEFAULT_UNIT, PUBLIC_HOMEPAGE, PUBLIC_SITE
from wagtail.wagtailcore.models import Page, Site
from file_parsing import is_int

def get_default_unit():
    """
    Get a fallback unit by ID from the config
    if no unit is set.

    Returns:
        UnitPage object
    """
    from units.models import UnitPage
    return UnitPage.objects.live().filter(id=DEFAULT_UNIT)[0]


def get_quick_num_or_link(dic):
    """
    Get the quick numbers or a link.

    Args:
        dic: A dictionary with the keys "label", "number"
        and "link", where values for label and number are
        strings. Values for link are either None or an
        integer representing a page ID.

    Returns:
        A tuple where the first item in either 0 or 1. 0
        represents a phone number and 1 represents a link.
        The second item in the tuple is a string label
        for display. If the first item is 0 then the third
        item is a string representing a phone number, if
        the first item is 1, then the thrid  is a string
        representing a url, e.g.:

        (0, 'Main Telephone', '773-702-8740') or
        (1, 'SCRC Contact Form', '/scrc/visiting/contact/')
    """

    assert all(k in dic for k in ['label', 'number', 'link']), \
        'Quick number dictionaries should have the following keys: label, number, link'

    assert dic['label'], 'There must always be a value for label'

    if dic['link']:
        assert is_int(dic['link']), \
            'The link key should contain an integer representing page ID'
        # relative_url gives an absolute url in unit tests, so, use get_url_parts instead
        retval = (1, dic['label'], Page.objects.all().get(id=dic['link']).get_url_parts()[-1])
    elif dic['number']:
        retval = (0, dic['label'], dic['number'])
    else:
        raise ValueError('Missing data: either a number or a link is required')

    return retval


def get_quick_num_html(quick_num):
    """
    Get the html for displaying a single quick number
    or link on the top of the public site directory.

    Args:
        dlist: a list of dictionaries formatted for the
        get_quick_num_or_link function.

        quick_num: a tuple representation of a quick
        number or link to be displayed at the top of
        the directory. The tuple should be of the same
        type returned from get_quick_num_or_link.

    Returns:
        html, representation of a quick number or link.
    """
    if quick_num[0] == 0:
        html = '<td><strong>' + quick_num[1] + '</strong> ' + quick_num[2] +'</td>'
    else:
        html = '<td><strong><a href="' + quick_num[2] + '">' + quick_num[1] + '</a></strong></td>'
    return html


def get_quick_nums(dlist):
    """
    Get all quick numbers and links for a given department
    to be displayed at the top of the public site unit
    directory listing.

    Args:
        dlist: a list of dictionaries formatted as required
        by get_quick_num_or_link.

    Returns:
        String, the full html to be displayed at the top of
        the department directory on the public site.
    """
    html = ''
    for item in dlist:
        html += get_quick_num_html(get_quick_num_or_link(item))
    return html
