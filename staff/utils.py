# -*- coding: utf-8 -*-
from __future__ import unicode_literals

#import os
#os.environ['DJANGO_SETTINGS_MODULE'] = 'library_website.settings'
import re

from base.utils import get_xml_from_directory_api
from django.contrib.auth.models import User
from django.db.models import F
from openpyxl import Workbook
from staff.models import EMPLOYEE_TYPES, POSITION_STATUS, StaffPage, StaffPageLibraryUnits
from units.models import UnitPage
from xml.etree import ElementTree

# need a list of all individuals. 
# this thing needs to deal with VCards. 

def get_all_library_cnetids_from_directory(xml_string = None):
    if not xml_string:
        xml_string = get_xml_from_directory_api('https://directory.uchicago.edu/api/v2/divisions/16.xml')

    # get xml element tree.
    x = ElementTree.fromstring(xml_string)

    # get cnetids.
    cnetids = set()
    for cnetid in x.findall(".//member/cnetid"):
        cnetids.add(cnetid.text)
    return sorted(list(cnetids))

def get_individual_info_from_directory(xml_string):
    x = ElementTree.fromstring(xml_string)

    info = {}

    info['cnetid'] = x.find("individuals/individual/cnetid").text

    # name is slightly more formal- e.g. "John E. Jung"
    info['officialName'] = x.find("individuals/individual/name").text

    # displayName is a bit more casual- e.g. "John Jung"
    info['displayName'] = x.find("individuals/individual/displayName").text

    #  title, department, subdepartment, building/room number, phone number:
    #  many individuals have more than one title- for example, 
    #  Emily Treptow has the following two strings as titles:
    #  "Business and Economics Librarian for Instruction & Outreach"
    #  "Business & Economics Librarian for Instruction & Outreach"
    #  Show both titles, even though they're close, to encourage
    #  people to fix them in the university's system. 
    #
    #  The title doesn't make sense without a department, subdepartment
    #  pair though. And many people, especially bibliographers, 
    #  have three or four title/department/subdepartments. 
    #
    # Also, some titles have different rooms- see Laura Ring for 
    # an example. Many of those people, like Paul Belloni, will 
    # have multiple phone numbers. (It looks like Paul has a phone
    # number at the SSA and at the Reg.)
    #
    # Each title gets it's own table? Each one points at a department/
    # subdepartment pair? (in it's own table...)

    info['title_department_subdepartments'] = set()
    info['title_department_subdepartments_dicts'] = []
    for vcard in x.findall("individuals/individual/contacts/contact"):
        try:
            if vcard.find('division/name').text != 'Library':
                continue
        except:
            continue
   
        output = [] 
        output_dict = {}

        try:
            title = re.sub('\s+', ' ', vcard.find('title').text).strip()
            if title:
                output.append(title)
                output_dict['title'] = title
        except:
            pass
        
        chunks = []
        try:      
            department = re.sub('\s+', ' ', vcard.find('department/name').text).strip()
            if department:
                chunks.append(department)
        except:
            pass

        try:
            subdepartment = re.sub('\s+', ' ', vcard.find('subDepartment/name').text).strip()
            if subdepartment:
                chunks = chunks + subdepartment.split(" | ")
        except:
            pass

        try:
            email = re.sub('\s+', ' ', vcard.find('email').text).strip()
            if email:
                output_dict['email'] = email
        except:
            pass

        try:
            facultyexchange = re.sub('\s+', ' ', vcard.find('facultyExchange').text).strip()
            if facultyexchange:
                output.append(facultyexchange)
                output_dict['facultyexchange'] = facultyexchange
        except:
            pass

        try:
            phone = re.sub('\s+', ' ', vcard.find('phone').text).strip()
            if phone:
                chunks = re.search('^\(([0-9]{3})\) ([0-9]{3})-([0-9]{4})$', phone)
                phone_number = chunks.group(1) + "-" + chunks.group(2) + "-" + chunks.group(3)
                output.append(phone_number)
                output_dict['phone'] = phone_number
        except:
            pass

        info['title_department_subdepartments'].add("\n".join(output))
        info['title_department_subdepartments_dicts'].append(output_dict)

    info['email'] = set()
    for vcard in x.findall("individuals/individual/contacts/contact"):
        try:
            if vcard.find('division/name').text != 'Library':
                continue
        except:
            continue

        try:
            email = re.sub('\s+', ' ', vcard.find('email').text).strip()
            if email:
                info['email'].add(email)
        except:
            pass

    info['phoneFacultyExchanges'] = set()
    info['phoneFacultyExchanges_dicts'] = []
    for vcard in x.findall("individuals/individual/contacts/contact"):
        try:
            if vcard.find('division/name').text != 'Library':
                continue
        except:
            continue
   
        output = [] 
        output_dict = {}

        try:
            facultyexchange = re.sub('\s+', ' ', vcard.find('facultyExchange').text).strip()
            if facultyexchange:
                output.append(facultyexchange)
                output_dict['facultyexchange'] = facultyexchange
        except:
            pass

        try:
            phone = re.sub('\s+', ' ', vcard.find('phone').text).strip()
            if phone:
                chunks = re.search('^\(([0-9]{3})\) ([0-9]{3})-([0-9]{4})$', phone)
                formatted_phone = chunks.group(1) + "-" + chunks.group(2) + "-" + chunks.group(3)
                output.append(formatted_phone)
                output_dict['phone'] = formatted_phone
        except:
            pass

        if output:
            info['phoneFacultyExchanges'].add("\n".join(output))
            info['phoneFacultyExchanges_dicts'].append(output_dict)

    info['positionTitle'] = ''
    for vcard in x.findall("individuals/individual/contacts/contact"):
        try:
            if vcard.find('division/name').text != 'Library':
                continue
        except:
            continue
   
        try:
            title = re.sub('\s+', ' ', vcard.find('title').text).strip()
            if title:
                info['positionTitle'] = title
                break
        except:
            pass

    return info

def get_all_library_cnetids_from_wagtail():
    output = []
    for s in StaffPage.objects.all():
        try:
            if User.objects.get(username=s.cnetid).is_active:
                output.append(s.cnetid)
        except:
            pass
    return output

# the data format changed with our 2017 update to the StaffPage object.
# instead of keeping VCards in bundles, now they are split into different
# pieces. 
#
# email addresses are repeatable but not bundled. units are repeatable
# but not bundled. phone numbers and faculty exchange are bundled together,
# and repeatable. 
#
# TODO: Add units. 
# 
def get_individual_info_from_wagtail(cnetid):
    staff_page = StaffPage.objects.get(cnetid=cnetid)

    if staff_page.display_name == None:
        raise ValueError(cnetid + ' has a display_name of None.')

    if staff_page.official_name == None:
        raise ValueError(cnetid + ' has an official_name of None.')
       
    # officialName is slightly more formal- e.g. "John E. Jung"
    # displayName is a bit more casual- e.g. "John Jung"
    output = {
        "cnetid": cnetid,
        "officialName": staff_page.official_name,
        "displayName": staff_page.display_name,
        "positionTitle": '',
        "email": set(),
        "departments": set(),
        "phoneFacultyExchanges": set()
    }

    for e in staff_page.staff_page_email.all():
        email_str = e.email.strip()
        if email_str:
            output['email'].add(email_str)

    if staff_page.position_title:
        output['positionTitle'] = re.sub('\s+', ' ', staff_page.position_title).strip()

    for v in staff_page.staff_page_phone_faculty_exchange.all():
        tmp = []

        faculty_exchange = v.faculty_exchange
        if faculty_exchange:
            tmp.append(re.sub('\s+', ' ', faculty_exchange).strip())

        phone_number = v.phone_number
        if phone_number:
            tmp.append(re.sub('\s+', ' ', phone_number).strip())

        if tmp:
            output['phoneFacultyExchanges'].add("\n".join(tmp))

    return output

def get_staff_wagtail(**options):
    staffpages = set()

    if options['all']:
        staffpages = set(StaffPage.objects.all())
    elif options['live']:
        staffpages = set(StaffPage.objects.live())

    if options['cnetid']:
        staffpages = set([StaffPage.objects.get(cnetid=options['cnetid'])])

    if options['department']:
        library_units = [u for u in UnitPage.objects.live() if u.get_full_name()==options['department']]
        new_staffpages = set(StaffPage.objects.filter(staff_page_units__library_unit__in=library_units))
        staffpages = staffpages.intersection(new_staffpages) if staffpages else new_staffpages

    if options['department_and_subdepartments']:
        library_units = set()
        for u in [u for u in UnitPage.objects.live() if u.get_full_name()==options['department_and_subdepartments']]:
            library_units = library_units.union(set(u.get_descendants(True).type(UnitPage).specific()))
        new_staffpages = set(StaffPage.objects.filter(staff_page_units__library_unit__in=list(library_units)))
        staffpages = staffpages.intersection(new_staffpages) if staffpages else new_staffpages

    if options['modified_since']:
        modified_since_string = '{}-{}-{} 00:00-0600'.format(options['modified_since'][0:4],
            options['modified_since'][4:6], options['modified_since'][6:8])
        new_staffpages = set(StaffPage.objects.filter(latest_revision_created_at__gte=modified_since_string))
        staffpages = staffpages.intersection(new_staffpages) if staffpages else new_staffpages

    if options['position_status']:
        position_status_int = [i for i, v in POSITION_STATUS if v == options['position_status']][0]
        new_staffpages = set(StaffPage.objects.filter(position_status=position_status_int))
        staffpages = staffpages.intersection(new_staffpages) if staffpages else new_staffpages

    if options['supervises_students']:
        new_staffpages = set(StaffPage.objects.filter(supervises_students=True))
        staffpages = staffpages.intersection(new_staffpages) if staffpages else new_staffpages

    if options['supervisor_cnetid']:
        new_staffpages = set(StaffPage.objects.get(cnetid=options['supervisor_cnetid']).get_staff())
        staffpages = staffpages.intersection(new_staffpages) if staffpages else new_staffpages

    if options['supervisor_override_set']:
        new_staffpages = set(StaffPage.objects.exclude(supervisor_override=None))
        staffpages = staffpages.intersection(new_staffpages) if staffpages else new_staffpages

    if options['title']:
        new_staffpages = set(StaffPage.objects.filter(position_title=options['title']))
        staffpages = staffpages.intersection(new_staffpages) if staffpages else new_staffpages

    return sorted(staffpages, key=lambda s: s.last_name)

def report_staff_wagtail(**options):
    staffpages = get_staff_wagtail(**options)
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append([
        'ID',
        'LATEST REVISION CREATED AT',
        'NAME AND CNETID',
        'POSITION TITLE',
        'EMAILS',
        'PHONE, FACEX',
        'UNITS',
        'EMPLOYEE TYPE',
        'SUPERVISES STUDENTS',
        'POSITION STATUS',
        'SUPERVISOR NAME AND CNETID'
    ])
    for s in staffpages:
        units = StaffPageLibraryUnits.objects.filter(page=s).values_list('library_unit__title', flat=True)

        try:
            latest_revision_created_at = s.latest_revision_created_at.strftime('%m/%d/%Y %-I:%M:%S %p')
        except AttributeError:
            latest_revision_created_at = ''

        name_and_cnetid = '%s (%s)' % (s.title, s.cnetid)

        supervisor_names_and_cnetids = ['%s (%s)' % (s.title, s.cnetid) for s in s.get_supervisors]

        emails = [e.email for e in s.staff_page_email.all()]

        phone_facexes = ['%s,%s' % (p.faculty_exchange, p.phone_number) for p in s.staff_page_phone_faculty_exchange.all()]

        employee_type_string = [v for i, v in EMPLOYEE_TYPES if i == s.employee_type][0]

        position_status_string = [v for i, v in POSITION_STATUS if i == s.position_status][0]

        worksheet.append([
            str(s.id),
            latest_revision_created_at,
            name_and_cnetid,
            s.position_title or '',
            '|'.join(emails) or '',
            '|'.join(phone_facexes) or '',
            '|'.join(units) or '',
            employee_type_string,
            str(s.supervises_students),
            position_status_string,
            '|'.join(supervisor_names_and_cnetids)
        ])
    return workbook





