# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64
import urllib.request
from xml.etree import ElementTree

from base.models import get_available_path_under, make_slug
from django.contrib.contenttypes.models import ContentType
from django.db import models, migrations
from http.client import HTTPSConnection
from intranethome.models import IntranetHomePage
from library_website.settings.local import DIRECTORY_USERNAME, DIRECTORY_PASSWORD
from staff.models import StaffIndexPage, StaffPage
from unidecode import unidecode
from wagtail.wagtailcore.models import Page

def get_all_library_cnetids():
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

def get_individual_info(cnetid):
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

    # email:
    #  Sarah Burgin has two jobs- an email address is only attached
    #  to one of them, the non-library job. Because of that I harvest
    #  all email addresses, not just ones attached to the library. In my 
    #  tests I only find one email address per person. 
    info['email'] = x.find("individuals/individual/contacts/contact/email").text

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

    info['title_department_subdepartments'] = []
    for vcard in x.findall("individuals/individual/contacts/contact"):
        try:
            if vcard.find('division/name').text != 'Library':
                continue
        except:
            continue
        title_department_subdepartment = {}
    
        try:
            title = vcard.find('title')
            title_department_subdepartment['title'] = title.text if title is not None else ''
               
            department = vcard.find('department/name') 
            title_department_subdepartment['department'] = department.text if department is not None else ''

            subdepartment = vcard.find('subDepartment/name')
            title_department_subdepartment['subdepartment'] = subdepartment.text if subdepartment is not None else ''

            facultyexchange = vcard.find('facultyExchange')
            title_department_subdepartment['facultyexchange'] = facultyexchange.text if facultyexchange is not None else ''

            phone = vcard.find('phone')
            title_department_subdepartment['phone'] = phone.text if phone is not None else ''
        except:
            print(cnetid)
            sys.exit()
        info['title_department_subdepartments'].append(title_department_subdepartment)

    return info

def create_staffindexpage(apps, schema_editor):
    StaffIndexPage = apps.get_model('staff.StaffIndexPage')
    staffindexpage_content_type = apps.get_model('contenttypes.ContentType').objects.get(model='staffindexpage', app_label='staff')

    # Get an available child path, like "00010002". 
    # Assume the intranet homepage has been set up already and that there is only one of them. 
    intranet_home_page_path = IntranetHomePage.objects.all()[0].path
    available_child_path = get_available_path_under(intranet_home_page_path)
        
    # copy code from the intranethomepage migration.
    # step through the children of the intranet homepage to find the next open slot. 
    # then do this same thing for each staff page. 
    # rather than find gaps, sort all of the paths under there, pop the last one off,
    # and add one to it to keep things simple. Fix it if it turns out to be a problem. 

    StaffIndexPage.objects.create(
        title='Staff',
        slug='staff',
        content_type=staffindexpage_content_type,
        path=available_child_path,
        depth=len(available_child_path) // 4,
        numchild=0,
        url_path='/staff/',
    )

def remove_staffindexpage(apps, schema_editor):
    StaffIndexPage = apps.get_model('staff.StaffIndexPage')
    for s in StaffIndexPage.objects.all():
        s.delete()

def create_staffpages(apps, schema_editor):
    staff_index_path = StaffIndexPage.objects.all()[0].path
    staff_index_depth = StaffIndexPage.objects.all()[0].depth
    staff_index_url = StaffIndexPage.objects.all()[0].url
    staff_index_content_type_pk = ContentType.objects.get(model='staffindexpage').pk
    staff_content_type_pk = ContentType.objects.get(model='staffpage').pk

    StaffPage = apps.get_model('staff.StaffPage')
    staffpage_content_type = apps.get_model('contenttypes.ContentType').objects.get(model='staffpage', app_label='staff')

    cnetids = get_all_library_cnetids()
    for cnetid in cnetids:
        info = get_individual_info(cnetid)
        next_available_path = get_available_path_under(staff_index_path)

        StaffPage.objects.create(
            title=info['displayName'],
            slug=make_slug(info['displayName']),
            content_type=staffpage_content_type,
            path=next_available_path,
            depth=len(next_available_path) // 4,
            numchild=0,
            url_path='/staff/' + make_slug(info['displayName']) + '/',
            cnetid=info['cnetid'],
            display_name=info['displayName'],
            official_name=info['officialName'],
            # first_name= (skip optional fields?)
            # middle_name= (skip optional fields?)
            #last_name= (skip optional fields?)
            #supervisor= (skip until later.)
            #profile_picture=... (skip optional fields?)
            #libguide_url=... (skip optional fields?)
            #bio=... (skip optional fields?)
            #cv=... (skip optional fields?)
            #is_public_persona=... (skip optional fields?)
        )

        # staff_vcard
        # Inside each vcard there is a pointer to the unit. get that in a second migration, once units have been installed.)
        ''' 
        VCard = apps.get_model("staff", "VCard")
   
        Deal with this stuff...
        vcards = []  
        # foreach vcard source as new vcard:
        vcards.append(VCard(
            email=info['email'],
            #phone_label (skip optional things?)
            phone_number="773-123-4567",
            title="Programmer",
            faculty_exchange="JRL 220", #(optional)
            #unit_id (skip optional things)
        ).save())
    
        # staff_staffpagepagevcards
        StaffPagePageVCards = apps.get_model("staff", "StaffPagePageVCards")
        for vcard in vcards:
            StaffPagePageVCards(
                vcard_ptr_id=vcard.id,
                #sort_order (skip optional things?)
                page_id=staffpage.id
            ).save()
        '''
    
        # skip StaffPageSubjectPlacement- people can add this themselves. 

def remove_staffpages(apps, schema_editor):
    StaffPage = apps.get_model('staff.StaffPage')
    for s in StaffPage.objects.all():
        s.delete()

class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0002_auto_20151113_2245'),
        ('intranethome', '0002_load_initial_homepage'),
    ]

    operations = [
        migrations.RunPython(create_staffindexpage, remove_staffindexpage),
        migrations.RunPython(create_staffpages, remove_staffpages),
    ]
