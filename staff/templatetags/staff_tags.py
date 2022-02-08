from django import template
from library_website.settings import BUILDINGS
from public.models import LocationPage, StaffPublicPage
from staff.utils import libcal_id_by_email

register = template.Library()


@register.filter
def ofKey(value, arg):
    if value:
        return value.get(arg)
    else:
        return ''


@register.inclusion_tag('staff/library_unit_links.html')
def library_unit_links(library_unit):
    try:
        library_unit_pieces = library_unit.get_full_name().split(' - ')
    except AttributeError:
        return {'units': []}
    units = []
    i = 0
    while i < len(library_unit_pieces):
        link_param = ' - '.join(library_unit_pieces[:i + 1])
        link_text = library_unit_pieces[i]
        units.append([link_param, link_text])
        i = i + 1
    return {'units': units}


@register.inclusion_tag('staff/staff_email_addresses.html')
def staff_email_addresses(staff_page):
    return {
        'emails':
        list(
            set(
                staff_page.staff_page_email.all().values_list(
                    'email', flat=True
                )
            )
        )
    }


@register.inclusion_tag('staff/staff_libcal_schedules.html')
def staff_libcal_schedules(staff_page):
    """
    Passes staff libcal information into the context for the Staff Page index
    view.

    Args:
        Wagtail page

    Output:
        Dictionary containing a list of all staff email addresses and
        a lookup table mapping email addresses to LibCalids

    """
    emails = list(
        set(staff_page.staff_page_email.all().values_list('email', flat=True))
    )

    return {
        'emails': emails,
    }


@register.inclusion_tag('staff/libcal_button.html')
def libcal_button(staff_page, email):
    """
    Given a staff page and an email address, inserts a libcal scheduler button
    for the staff member whose email address that is into a template.

    Args:
        Staff page, Email address (string)

    Output:
        Staff member's libcal id

    """
    libcal_id = libcal_id_by_email(email)

    return {
        'libcal_id': libcal_id,
    }


@register.inclusion_tag('staff/staff_faculty_exchanges_phone_numbers.html')
def staff_faculty_exchanges_phone_numbers(staff_page):
    libraries = {
        'JCL': LocationPage.objects.get(title=BUILDINGS[0][1]),
        'JRL': LocationPage.objects.get(title=BUILDINGS[4][1]),
        'LBQ': LocationPage.objects.get(title=BUILDINGS[1][1]),
        'Mansueto': LocationPage.objects.get(title=BUILDINGS[3][1]),
        'MAN': LocationPage.objects.get(title=BUILDINGS[3][1]),
        'SSA': LocationPage.objects.get(title=BUILDINGS[6][1]),
        'RY': LocationPage.objects.get(title=BUILDINGS[7][1]),
        'E': LocationPage.objects.get(title=BUILDINGS[2][1]),
    }

    lib_room_phone = []
    for p in staff_page.staff_page_phone_faculty_exchange.all():
        library_abbreviation = p.faculty_exchange.split(' ')[0]
        if library_abbreviation in libraries:
            lib = libraries[library_abbreviation]
        else:
            lib = None

        try:
            room = p.faculty_exchange.split(' ')[1]
        except IndexError:
            room = None

        phone = None
        if p.phone_number:
            phone = p.phone_number

        lib_room_phone.append([lib, room, phone])

    return {'lib_room_phone': lib_room_phone}


@register.inclusion_tag('staff/staff_subjects.html')
def staff_subjects(staff_page):
    subjects = []
    for s in staff_page.staff_subject_placements.all():
        subjects.append(s.subject.name)

    return {'subjects': sorted(subjects)}


@register.inclusion_tag('staff/staff_public_page_link.html')
def staff_public_page_link(staff_page):
    try:
        href = StaffPublicPage.objects.get(cnetid=staff_page.cnetid).url
    except(AttributeError, StaffPublicPage.DoesNotExist):
        href = ''

    return {'href': href, 'title': staff_page.title}
