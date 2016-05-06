from django import template

register = template.Library()

@register.inclusion_tag('units/staff_email_addresses.html')
def staff_email_addresses(staff_page):
    return {
        'emails': list(set(staff_page.vcards.all().values_list('email', flat=True)))
    }

@register.inclusion_tag('units/staff_faculty_exchanges_phone_numbers.html')
def staff_faculty_exchanges_phone_numbers(staff_page):
    facex_phone_pairs = set()
    for vcard in staff_page.vcards.all():
        facex_phone_pairs.add(vcard.faculty_exchange + '\t' + vcard.phone_number)
    
    facex_phone_pairs_list = sorted(list(map(lambda p: p.split('\t'), list(facex_phone_pairs))), key=lambda p: p[0])
    
    return {
        'facex_phone_pairs': facex_phone_pairs_list
    }
    
