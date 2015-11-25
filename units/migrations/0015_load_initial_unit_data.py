# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64

from base.models import get_available_path_under, make_slug
from django.db import migrations, models
from http.client import HTTPSConnection
from intranethome.models import IntranetHomePage
from library_website.settings.local import DIRECTORY_USERNAME, DIRECTORY_PASSWORD
from xml.etree import ElementTree

# each /responseData/organizations/organization/departments/department
# has a <name> and <xmlURL>
# e.g.  https://directory.uchicago.edu/api/v2/departments/241

# those things have /responseData/organizations/organization/subDepartments/subDepartment
# have <name and <xmlURL>
# e.g. https://directory.uchicago.edu/api/v2/subdepartments/1093

# those subdepartments have lists of people- 
# /responseData/organizations/organization/members/member
# each of those has a cnetid. 
# do these subdepartments ever nest or do they just have members?) 

def get_library_departments():
    c = HTTPSConnection("directory.uchicago.edu")
    b = bytes(DIRECTORY_USERNAME + ':' + DIRECTORY_PASSWORD, 'utf-8')
    userAndPass = base64.b64encode(b).decode("ascii")
    headers = { 'Authorization' : 'Basic %s' %  userAndPass } 
    c.request('GET', '/api/v2/divisions/16.xml', headers=headers)
    result = c.getresponse()

    # get xml element tree.
    x = ElementTree.fromstring(result.read())

    departments = []
    for department in x.findall(".//department"):
        departments.append({
            "url": department.find("resources/xmlURL").text,
            "name": department.find("name").text
        })
    return departments

def get_department_subdepartments(url):
    url = url.replace("https://directory.uchicago.edu", "")
    
    c = HTTPSConnection("directory.uchicago.edu")
    b = bytes(DIRECTORY_USERNAME + ':' + DIRECTORY_PASSWORD, 'utf-8')
    userAndPass = base64.b64encode(b).decode("ascii")
    headers = { 'Authorization' : 'Basic %s' %  userAndPass } 
    c.request('GET', url, headers=headers)
    result = c.getresponse()

    # get xml element tree.
    x = ElementTree.fromstring(result.read())

    subdepartments = []

    # first round. For subdepartment names without a pipe, 
    # just record them. For subdepartment names with a pipe,
    # record the first part only. 
    for subdepartment in x.findall(".//subDepartment"):
        subd_name = subdepartment.find("name").text
        if "|" in subd_name:
            continue

        subd_url = subdepartment.find("resources/xmlURL").text

        subdepartments.append({
            "name": subd_name,
            "url": subd_url,
            "children": []
        })

    # second round. Skip subdepartment names without a pipe.
    # throw an error for subdepartment names with two or more
    # pipes. Otherwise, add children to the subdepartments
    # dictionary in the appropriate place. 
    for subdepartment in x.findall(".//subDepartment"):
        subd_name = subdepartment.find("name").text
        if not "|" in subd_name:
            continue

        subd_url = subdepartment.find("resources/xmlURL").text

        subd1_name = subd_name.split("|").pop(0).strip()

        subd2_name = subd_name.split("|").pop().strip()
        if "|" in subd2_name:
            raise ValueError 

        subd2_url  = subd_url

        for s in subdepartments:
            if s["name"] == subd1_name:
                s["children"].append({
                    "name": subd2_name,
                    "url": subd2_url,
                    "children": []
                })
                break

    return subdepartments

def get_subdepartment_members(url):
    url = url.replace("https://directory.uchicago.edu", "")
    
    c = HTTPSConnection("directory.uchicago.edu")
    b = bytes(DIRECTORY_USERNAME + ':' + DIRECTORY_PASSWORD, 'utf-8')
    userAndPass = base64.b64encode(b).decode("ascii")
    headers = { 'Authorization' : 'Basic %s' %  userAndPass } 
    c.request('GET', url, headers=headers)
    result = c.getresponse()

    # get xml element tree.
    x = ElementTree.fromstring(result.read())

    cnetids = []
    for member in x.findall(".//member"):
        cnetids.append(member.find("cnetid").text)
    return sorted(cnetids)

def create_unitindexpage(apps, schema_editor):
    UnitIndexPage = apps.get_model('units.UnitIndexPage')
    unitindexpage_content_type = apps.get_model('contenttypes.ContentType').objects.get(model='unitindexpage', app_label='units')

    # Get an available child path, like "00010002". 
    # Assume the intranet homepage has been set up already and that there is only one of them. 
    intranet_home_page_path = IntranetHomePage.objects.all()[0].path
    available_child_path = get_available_path_under(intranet_home_page_path)

    UnitIndexPage.objects.create(
        title='Units',
        slug='units',
        content_type=unitindexpage_content_type,
        path=available_child_path,
        depth=len(available_child_path) // 4,
        numchild=0,
        url_path='/units/',
    )

def remove_unitindexpage(apps, schema_editor):
    UnitIndexPage = apps.get_model('units.UnitIndexPage')
    for u in UnitIndexPage.objects.all():
        u.delete()

def create_unitpages(apps, schema_editor):
    UnitIndexPage = apps.get_model('units.UnitIndexPage')
    unit_index_path = UnitIndexPage.objects.all()[0].path
    
    UnitPage = apps.get_model('units.UnitPage')
    unitpage_content_type = apps.get_model('contenttypes.ContentType').objects.get(model='unitpage', app_label='units')

    departments = get_library_departments()
    for d in departments:
        url = d["url"]
        name = d["name"]
        path = get_available_path_under(unit_index_path)

        new_unitpage = UnitPage.objects.create(
            title=name,
            slug=make_slug(name),
            content_type=unitpage_content_type,
            path=path,
            depth=len(path) // 4,
            numchild=0,
            url_path='/units/' + make_slug(name) + '/',
        )

        subdepartments = get_department_subdepartments(url)
        for subd in subdepartments:
            subd_url = subd["url"]
            subd_name = subd["name"]
            subd_path = get_available_path_under(new_unitpage.path)

            new_subunitpage = UnitPage.objects.create(
                title=subd_name,
                slug=make_slug(subd_name),
                content_type=unitpage_content_type,
                path=subd_path,
                depth=len(subd_path) // 4,
                numchild=0,
                url_path='/units/' + make_slug(name) + '/' + make_slug(subd_name) + '/',
            )

            for child in subd["children"]:
                child_path = get_available_path_under(new_subunitpage.path)
                UnitPage.objects.create(
                    title=child["name"],
                    slug=make_slug(child["name"]),
                    content_type=unitpage_content_type,
                    path=child_path,
                    depth=len(child_path) // 4,
                    numchild=0,
                    url_path='/units/' + make_slug(name) + '/' + make_slug(subd_name) + '/' + make_slug(child["name"]) + '/'
                )

def remove_unitpages(apps, schema_editor):
    UnitPage = apps.get_model('units.UnitPage')
    for u in UnitPage.objects.all():
        u.delete()

class Migration(migrations.Migration):

    dependencies = [
        ('units', '0014_unitindexpage'),
        ('intranethome', '0002_load_initial_homepage'),
    ]

    operations = [
        migrations.RunPython(create_unitindexpage, remove_unitindexpage),
        migrations.RunPython(create_unitpages, remove_unitpages),
    ]

