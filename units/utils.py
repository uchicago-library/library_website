from base.utils import get_xml_from_directory_api
from django.conf import settings
from django.db.models.base import ObjectDoesNotExist
from django.utils.text import slugify
from file_parsing import is_int
from library_website.settings import DEFAULT_UNIT, PUBLIC_HOMEPAGE, PUBLIC_SITE
from wagtail.wagtailcore.models import Page, Site
from xml.etree import ElementTree

import re

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


def get_all_quick_nums_html(dlist):
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


def get_quick_nums_for_library_or_dept(request):
    """
    Gets the quick number html for a request by library or 
    department (unit). The following precedence is observed:
    
    1. If "library" is present in the request and config, it is used.
    2. If "department" is present in the request and the config, it 
       is used.
    3. If "department" is in the request but not in the config, 
       unit > location is used.
    4. If nothing is found, the default fallback of library will
       be used.

    Args:
        dlist: a list of dictionaries formatted as required
        by get_quick_num_or_link.

        request: object

    Returns:
        String, the full html to be displayed at the top of
        the department directory chosen by the available data.
    """
    library = request.GET.get('library', None)
    department = request.GET.get('department', None)
    fallback = slugify('the-university-of-chicago-library')

    assert fallback in settings.QUICK_NUMS, '"the-university-of-chicago-library" is a required key in the "QUICK_NUMS" dictionary'
    html = get_all_quick_nums_html(settings.QUICK_NUMS[fallback])
    if library:
        html = get_all_quick_nums_html(settings.QUICK_NUMS[slugify(library)])
    elif department:
        try:
            html = get_all_quick_nums_html(settings.QUICK_NUMS[slugify(department)])
        except(KeyError):
            from units.models import UnitIndexPage, UnitPage
            url_path = UnitIndexPage.objects.first().url_path + '/'.join(map(slugify, department.split(' - '))) + '/'
            try:
                unitpage = UnitPage.objects.live().get(url_path=url_path)
                html = get_all_quick_nums_html(settings.QUICK_NUMS[slugify(unitpage.location)])
            except(UnitPage.DoesNotExist, AssertionError, KeyError):
                pass
    return html

def units_out_of_sync():
    """
    Get lists of unit pages that are out of sync.

    This function returns two lists--first, a list of the names of unit pages
    that are present in Wagtail, but missing in the campus directory. Second,
    a list of the names of unit pages that are present in the campus directory
    but missing in Wagtail.

    Note: We have to return names in the style of the campus directory (like
    those returned by the UnitPage's get_campus_directory_full_name() method)
    because we may only have access to a given unit in the campus directory. If
    that's the case it would be impossible to tell what its full name might be
    in the library directory.

    Returns: two lists of strings.
    """
    from units.models import UnitPage
    api_unit_names = get_campus_directory_unit_names()
    wag_unit_names = set()

    for u in UnitPage.objects.filter(
        display_in_campus_directory=True,
        live=True
    ):
        wag_unit_names.add(u.get_campus_directory_full_name())

    missing_in_campus_directory = sorted(
        list(api_unit_names.difference(wag_unit_names))
    )
    missing_in_wagtail = sorted(
        list(wag_unit_names.difference(api_unit_names))
    )
    return missing_in_campus_directory, missing_in_wagtail

def get_campus_directory_unit_names():
    """
    Report unit names in the campus directory.

    Returns:
        a set() of campus directory full names, as strings.
    """
    unit_names = set()
    x = ElementTree.fromstring(
        get_xml_from_directory_api('https://directory.uchicago.edu/api/v2/divisions/16')
    )
    for d in x.findall(".//departments/department"):
        department_name = re.sub(
            '\s+',
            ' ',
            d.find('name').text
        ).strip()
        unit_names.add(department_name)
        department_xml = d.find('resources/xmlURL').text
        x2 = ElementTree.fromstring(
            get_xml_from_directory_api(department_xml)
        )
        for d2 in x2.findall(".//subDepartments/subDepartment"):
            subdepartment_name = re.sub(
                '\s+',
                ' ',
                d2.find('name').text
            ).strip()
            unit_names.add(department_name + ' - ' + subdepartment_name)
    return unit_names

def add_units_out_of_sync_worksheet(workbook):
    """
    Adds a report of the units that are present in Wagtail but not in the
    campus directory, and vice versa, to a Microsoft Excel spreadsheet.

    Arguments:
        An OpenPyXL Workbook.

    Side Effect:
        Adds an OpenPyXL worksheet with information about out of sync units. 
    """
    cu, wu = units_out_of_sync()
    worksheet = workbook.create_sheet(title='units out of sync')
    if wu:
        worksheet.append(["THE FOLLOWING UNITS APPEAR IN WAGTAIL, BUT NOT THE UNIVERSITY'S API:"])
        for w in wu:
            worksheet.append([w])
        worksheet.append([""])
    if cu:
        worksheet.append(["THE FOLLOWING UNITS APPEAR IN THE UNIVERSITY'S API, BUT NOT WAGTAIL:"])
        for c in cu:
            worksheet.append([c])
        worksheet.append([""])

def get_units_wagtail(**options):
    """
    Query for a list of UnitPage objects. The options passed to this function
    basically get applied as a Django filter().

    Returns:
        A sorted list of UnitPage objects.
    """
    from units.models import UnitPage
    try:
        if options['live']:
            unitpages = set(UnitPage.objects.live())
        else:
            unitpages = set(UnitPage.objects.all())
    except KeyError:
        unitpages = set(UnitPage.objects.all())

    try:
        if options['latest_revision_created_at']:
            latest_revision_created_at_string = '{}-{}-{} 00:00-0600'.format(options['latest_revision_created_at'][0:4],
                options['latest_revision_created_at'][4:6], options['latest_revision_created_at'][6:8])
            new_unitpages = set(UnitPage.objects.filter(latest_revision_created_at__gte=latest_revision_created_at_string))
            unitpages = unitpages.intersection(new_unitpages) if unitpages else new_unitpages
    except KeyError:
        pass

    try:
        if options['display_in_campus_directory']:
            new_unitpages = set(UnitPage.objects.filter(display_in_campus_directory=True))
            unitpages = unitpages.intersection(new_unitpages) if unitpages else new_unitpages
    except KeyError:
        pass

    return sorted(list(unitpages), key=lambda u: u.get_full_name())

def add_wagtail_units_report_worksheet(workbook, **options):
    """
    Get a report of library units in Microsoft Excel format, for HR reporting.

    Returns:
        An OpenPyXL Workbook.
    """
    unitpages = get_units_wagtail(**options)
    worksheet = workbook.create_sheet(title='wagtail units')
    worksheet.append([
        'ID',
        'LATEST REVISION CREATED AT',
        'LIBRARY DIRECTORY FULL NAME',
        'CAMPUS DIRECTORY FULL NAME'
    ])
    for u in unitpages:
        try:
            latest_revision_created_at = u.latest_revision_created_at.strftime('%m/%d/%Y %-I:%M:%S %p')
        except AttributeError:
            latest_revision_created_at = ''
        worksheet.append([
            str(u.id),
            latest_revision_created_at,
            u.get_full_name(),
            u.get_campus_directory_full_name()
        ])
