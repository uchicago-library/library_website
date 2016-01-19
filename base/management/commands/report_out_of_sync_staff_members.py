# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand

import base64
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'library_website.settings'
import re
import sys

from directory_unit.models import DirectoryUnit
from django.contrib.auth.models import User
from django.db.models import F
from http.client import HTTPSConnection
from library_website.settings.local import DIRECTORY_USERNAME, DIRECTORY_PASSWORD
from staff.models import StaffPage
from xml.etree import ElementTree

# need a list of all individuals. 
# this thing needs to deal with VCards. 

def get_all_library_cnetids_from_directory():
    c = HTTPSConnection("directory.uchicago.edu")
    b = bytes(DIRECTORY_USERNAME + ':' + DIRECTORY_PASSWORD, 'utf-8')
    userAndPass = base64.b64encode(b).decode("ascii")
    headers = { 'Authorization' : 'Basic %s' %  userAndPass } 
    c.request('GET', '/api/v2/divisions/16.xml', headers=headers)
    result = c.getresponse()

    # get xml element tree.
    x = ElementTree.fromstring(result.read())

    # get cnetids.
    cnetids = set()
    for cnetid in x.findall(".//member/cnetid"):
        cnetids.add(cnetid.text)
    return sorted(list(cnetids))

def get_individual_info_from_directory(cnetid):
    info = {
        "cnetid": cnetid
    }

    c = HTTPSConnection("directory.uchicago.edu")
    b = bytes(DIRECTORY_USERNAME + ':' + DIRECTORY_PASSWORD, 'utf-8')
    userAndPass = base64.b64encode(b).decode("ascii")
    headers = { 'Authorization' : 'Basic %s' %  userAndPass } 
    c.request('GET', "/api/v2/individuals/" + cnetid + ".xml", headers=headers)
    result = c.getresponse()

    # get xml element tree.
    x = ElementTree.fromstring(result.read())

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
    for vcard in x.findall("individuals/individual/contacts/contact"):
        try:
            if vcard.find('division/name').text != 'Library':
                continue
        except:
            continue
   
        output = [] 

        try:
            title = re.sub('\s+', ' ', vcard.find('title').text).strip()
            if title:
                output.append(title)
        except:
            pass
        
        try:      
            department = re.sub('\s+', ' ', vcard.find('subDepartment/name').text).strip()
            if department:
                output.append(department.split(" | ").pop())
        except:
            pass

        try:
            facultyexchange = re.sub('\s+', ' ', vcard.find('facultyExchange').text).strip()
            if facultyexchange:
                output.append(facultyexchange)
        except:
            pass

        try:
            phone = re.sub('\s+', ' ', vcard.find('phone').text).strip()
            if phone:
                chunks = re.search('^\(([0-9]{3})\) ([0-9]{3})-([0-9]{4})$', phone)
                output.append(chunks.group(1) + "-" + chunks.group(2) + "-" + chunks.group(3))
        except:
            pass

        info['title_department_subdepartments'].add("\n".join(output))

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

class Command (BaseCommand):
    """
    Report staff members and VCards that are out of sync between the University directory and Wagtail.

    Example: 
        python manage.py report_out_of_sync_staff_members
    """

    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement this 
        method. It may return a Unicode string which will be printed to 
        stdout. More: https://docs.djangoproject.com/en/1.8/howto/custom
        -management-commands/#django.core.management.BaseCommand.handle
        """

        # api staff, wagtail staff
        api_staff = set(get_all_library_cnetids_from_directory())
        wag_staff = set(get_all_library_cnetids_from_wagtail())

        output = []

        missing_in_api = wag_staff.difference(api_staff)
        if missing_in_api:
            output.append("THE FOLLOWING STAFF APPEAR IN WAGTAIL, BUT NOT IN THE UNIVERSITY'S API:")
            output = output + list(missing_in_api)
            # if this happens, go into the user object and mark is_active False. 

        missing_in_wagtail = api_staff.difference(wag_staff)
        if missing_in_wagtail:
            output.append("THE FOLLOWING STAFF APPEAR IN THE UNIVERSITY'S API, BUT NOT IN WAGTAIL:")
            output = output + list(missing_in_wagtail)
            # if this happens, report that a new user needs to be created.

        for s in sorted(list(api_staff.intersection(wag_staff))):
            api = get_individual_info_from_directory(s)
            wag = get_individual_info_from_wagtail(s)

            if not api['officialName'] == wag['officialName']:
                output.append(s + "'s officialName is " + api['officialName'] + ", not " + wag['officialName'])

            if not api['displayName'] == wag['displayName']:
                output.append(s + "'s displayName is " + api['displayName'] + ", not " + wag['displayName'])
                # In the user management command, change the following things in the User object:
                # (note- in the User object, username = cnetid)
                # prompt a human for first_name, last_name.
                # In the StaffPage object,
                # check displayName and officialName.

            diffs = api['title_department_subdepartments'].difference(wag['title_department_subdepartments'])
            if diffs:
                output.append("THE FOLLOWING VCARDS APPEAR FOR " + s + " IN THE UNIVERSITY'S API, BUT NOT IN WAGTAIL:")
                for d in diffs:
                    output.append(d)

            diffs = wag['title_department_subdepartments'].difference(api['title_department_subdepartments'])
            if diffs:
                output.append("THE FOLLOWING VCARDS APPEAR FOR " + s + " IN WAGTAIL, BUT NOT IN THE UNIVERSITY'S API:")
                for d in diffs:
                    output.append(d)

        return "\n".join(output)
    


