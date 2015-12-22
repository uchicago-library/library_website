# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'library_website.settings'
import sys

from http.client import HTTPSConnection
from library_website.settings.local import DIRECTORY_USERNAME, DIRECTORY_PASSWORD
from xml.etree import ElementTree

from directory_unit.models import DirectoryUnit

def get_full_name(directory_unit):
    if directory_unit.name == 'Library':
        return 'Library'
    full_name = []
    while True:
        if directory_unit == None:
            break
        if directory_unit.name == 'Library':
            break
        full_name.append(directory_unit.name)
        directory_unit = directory_unit.parentUnit
    return " - ".join(list(reversed(full_name)))
    
def load_directoryunits(xml):
    xml_path = xml.replace('https://directory.uchicago.edu', '')
    print(xml)
    c = HTTPSConnection("directory.uchicago.edu")
    b = bytes(DIRECTORY_USERNAME + ':' + DIRECTORY_PASSWORD, 'utf-8')
    userAndPass = base64.b64encode(b).decode("ascii")
    headers = { 'Authorization' : 'Basic %s' %  userAndPass } 
    c.request('GET', xml_path, headers=headers)
    result = c.getresponse()

    # get xml element tree.
    x = ElementTree.fromstring(result.read())

    # no matter what, name is in the same place.
    name = x.find(".//organizations/organization/name").text
    print(name)

    if xml.find("/divisions/") > -1:
        parentUnit = None
        if DirectoryUnit.objects.filter(name=name, parentUnit=None, xmlUrl=xml).count() == 0:
            DirectoryUnit.objects.create(
                name=name,
                parentUnit=None,
                xmlUrl=xml
            )
        for d in x.findall(".//departments/department/resources/xmlURL"):
            load_directoryunits(d.text)
    elif xml.find("/departments/") > -1:
        parentXml = x.find(".//division/resources/xmlURL").text
        parentUnit = DirectoryUnit.objects.get(xmlUrl=parentXml)
        if DirectoryUnit.objects.filter(name=name, parentUnit=parentUnit, xmlUrl=xml).count() == 0:
            DirectoryUnit.objects.create(
                name=name,
                parentUnit=parentUnit,
                xmlUrl=xml
            )
        for d in x.findall(".//subDepartments/subDepartment/resources/xmlURL"):
            load_directoryunits(d.text)
    elif xml.find("/subdepartments/") > -1:
        print("/subdepartments/")
        chunks = list(map(lambda s: s.strip(), name.split("|")))
        print(chunks)

        # if this happens I'll need to rewrite the code below. 
        if len(chunks) > 2:
            print(name + " has more than one pipe.")
            sys.exit()

        firstChunkParentXml = x.find(".//department/resources/xmlURL").text
        firstChunkParentUnit = DirectoryUnit.objects.get(xmlUrl=firstChunkParentXml)
        if DirectoryUnit.objects.filter(name=chunks[0], parentUnit=firstChunkParentUnit).count() == 0:
            print("FIRST CHUNK: " + chunks[0])
            DirectoryUnit.objects.create(
                name=chunks[0],
                parentUnit=firstChunkParentUnit,
                xmlUrl=xml
            )

        if len(chunks) > 1:
            firstChunkUnit = DirectoryUnit.objects.filter(name=chunks[0], parentUnit=firstChunkParentUnit)[0]
            if DirectoryUnit.objects.filter(name=chunks[1], parentUnit=firstChunkUnit, xmlUrl=xml).count() == 0:
                print("SECOND CHUNK: " + chunks[1])
                DirectoryUnit.objects.create(
                    name=chunks[1],
                    parentUnit=firstChunkUnit,
                    xmlUrl=xml
                )

#DirectoryUnit.objects.all().delete()
load_directoryunits("https://directory.uchicago.edu/api/v2/divisions/16")
for d in DirectoryUnit.objects.all():
    d.fullName = get_full_name(d)
    d.save()

