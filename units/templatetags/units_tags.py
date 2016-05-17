from django import template
from public.models import LocationPage
from staff.models import StaffPage

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
    
    facex_phone_pairs_list = list(map(lambda p: p.split('\t'), list(facex_phone_pairs)))

    lib_room_phone = []
    for p in facex_phone_pairs_list:
        facex_parts = p[0].split(' ')
       
        lib = '' 
        if facex_parts[0] == 'JCL':     
            lib = LocationPage.objects.get(title='The John Crerar Library')
        elif facex_parts[0] == 'JRL':
            lib = LocationPage.objects.get(title='The Joseph Regenstein Library')
        elif facex_parts[0] == 'LBQ':
            lib = None
        elif facex_parts[0] in ['MAN', 'Mansueto']:
            lib = LocationPage.objects.get(title='The Joe and Rika Mansueto Library')
        elif facex_parts[0] == 'SSA':
            lib = LocationPage.objects.get(title='Social Service Administration Library')
        else:
            lib = None

        if len(facex_parts) > 1:
            room = facex_parts[1]
        else:
            room = None

        if p[1]:
            phone = p[1]
        else:
            phone = None
       
        lib_room_phone.append([lib, room, phone])
    
    return {
        'lib_room_phone': lib_room_phone
    }
    
@register.inclusion_tag('units/staff_subjects.html')
def staff_subjects(staff_page):
    subjects = []
    for s in staff_page.staff_subject_placements.all():
        subjects.append(s.subject.name)
    
    return {
        'subjects': sorted(subjects)
    }
    
