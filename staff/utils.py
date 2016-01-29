# -*- coding: utf-8 -*-
from __future__ import unicode_literals

#import os
#os.environ['DJANGO_SETTINGS_MODULE'] = 'library_website.settings'
import re

from base.utils import get_xml_from_directory_api
from directory_unit.models import DirectoryUnit
from django.contrib.auth.models import User
from django.db.models import F
from staff.models import StaffPage
from xml.etree import ElementTree

# need a list of all individuals. 
# this thing needs to deal with VCards. 

def get_all_library_cnetids_from_directory():
    # get xml element tree.
    x = ElementTree.fromstring(get_xml_from_directory_api('https://directory.uchicago.edu/api/v2/divisions/16.xml'))

    # get cnetids.
    cnetids = set()
    for cnetid in x.findall(".//member/cnetid"):
        cnetids.add(cnetid.text)
    return sorted(list(cnetids))

def get_individual_info_from_directory(cnetid):
    info = {
        "cnetid": cnetid
    }

    # get xml element tree.
    x = ElementTree.fromstring(get_xml_from_directory_api('https://directory.uchicago.edu/api/v2/individuals/' + cnetid + '.xml'))

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

        if chunks:
            parent_unit = DirectoryUnit.objects.get(name='Library')
            c = 0
            while c < len(chunks):
                unit = DirectoryUnit.objects.get(parentUnit=parent_unit, name=chunks[c])
                parent_unit = unit
                c = c + 1 
            output_dict['department'] = unit.pk
            output.append(chunks.pop())

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

def get_individual_info_from_wagtail(cnetid):
    # deal with the case of Scooter Mc Danger here. Make sure the display_name and title are equal. 
    staff_page = StaffPage.objects.get(cnetid=cnetid, title=F('display_name'))
       
    # officialName is slightly more formal- e.g. "John E. Jung"
    # displayName is a bit more casual- e.g. "John Jung"
    output = {
        "cnetid": cnetid,
        "officialName": staff_page.official_name,
        "displayName": staff_page.display_name,
        "title_department_subdepartments": set()
    }

    for v in staff_page.vcards.all():
        tmp = []

        title = v.title
        if title:
            tmp.append(re.sub('\s+', ' ', title).strip())

        department = v.unit.name
        if department:
            tmp.append(re.sub('\s+', ' ', department).strip())

        facultyexchange = v.faculty_exchange
        if facultyexchange:
            tmp.append(re.sub('\s+', ' ', facultyexchange).strip())

        phone = v.phone_number
        if phone:
            tmp.append(re.sub('\s+', ' ', phone).strip())

        output['title_department_subdepartments'].add("\n".join(tmp))

    return output


