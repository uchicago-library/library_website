from django import template
from units.models import BUILDINGS

register = template.Library()


@register.filter
def ofKey(value, arg):
    if value:
        return value.get(arg)
    else:
        return ''


@register.simple_tag
def department_building_room(unit_page):
    building_room_pieces = []
    for b in BUILDINGS:
        if b[0] == unit_page.building:
            building_room_pieces.append(b[1])

    room_number_pieces = unit_page.room_number.split(' ')
    if len(room_number_pieces) == 2:
        building_room_pieces.append('Room ' + room_number_pieces[1])

    return ', '.join(building_room_pieces)


@register.simple_tag
def department_contact_info(unit_page):
    output = []

    for p in unit_page.unit_page_phone_number.all():
        if p.phone_label:
            output.append('{}: {}'.format(p.phone_label, p.phone_number))
        else:
            output.append(p.phone_number)

    if unit_page.fax_number:
        output.append('Fax: {}'.format(unit_page.fax_number))

    if unit_page.email:
        if unit_page.email_label:
            output.append(
                '<a href="mailto:{}">{}</a>'.format(
                    unit_page.email, unit_page.email_label
                )
            )
        else:
            output.append(
                '<a href="mailto:{}">{}</a>'.format(unit_page.email, unit_page.email)
            )

    if unit_page.link_external:
        if unit_page.link_text:
            output.append(
                '<a href="{}">{}</a>'.format(
                    unit_page.link_external, unit_page.link_text
                )
            )
        else:
            output.append(
                '<a href="{}">{}</a>'.format(
                    unit_page.link_external, unit_page.link_external
                )
            )

    if unit_page.link_page:
        if unit_page.link_text:
            output.append(
                '<a href="{}">{}</a>'.format(
                    unit_page.link_page.url, unit_page.link_text
                )
            )
        else:
            output.append(
                '<a href="{}">{}</a>'.format(
                    unit_page.link_page.url, unit_page.link_page.url
                )
            )

    if unit_page.link_document:
        if unit_page.link_text:
            output.append(
                '<a href="{}">{}</a>'.format(
                    unit_page.link_document.url, unit_page.link_text
                )
            )
        else:
            output.append(
                '<a href="{}">{}</a>'.format(
                    unit_page.link_document.url, unit_page.link_document.url
                )
            )

    if unit_page.public_web_page:
        output.append(
            '<a href="{}">{}</a>'.format(
                unit_page.public_web_page.url, unit_page.public_web_page.title
            )
        )

    return '<br/>'.join(output)


@register.simple_tag
def division_building_room_phone(unit_page):
    building_room_phone = []

    building_room_string = department_building_room(unit_page)
    if building_room_string:
        building_room_phone.append(building_room_string)

    phone_number = ''
    try:
        phone_number = unit_page.unit_page_phone_number.first().phone_number
    except:
        pass

    if phone_number:
        building_room_phone.append(phone_number)

    return ' &nbsp; | &nbsp; '.join(building_room_phone)


@register.simple_tag
def get_division(unit_page):
    from units.models import UnitPage

    division = unit_page.get_ancestors().type(UnitPage).first()
    if division == unit_page:
        return None
    else:
        return division
