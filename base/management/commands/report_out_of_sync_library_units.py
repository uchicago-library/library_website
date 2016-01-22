# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand

import base64
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'library_website.settings'
import sys

from http.client import HTTPSConnection
from intranetunits.models import IntranetUnitsPage
from library_website.settings.local import DIRECTORY_USERNAME, DIRECTORY_PASSWORD
from xml.etree import ElementTree

from directory_unit.models import DirectoryUnit

def walk(node):
    yield node 
    for child in node['children']:
        for n in walk(child):
            yield n

def find_node_for_xml(node, xml):
    for n in walk(node):
        if n['xml'] == xml:
            return n

def find_parent_for_xml(node, xml):
    for n in walk(node):
        if xml in list(map(lambda c: c['xml'], n['children'])):
            return n

def get_full_name_for_node(tree, node):
    full_name = []
    while True:
        full_name.insert(0, node['name'])
        node = find_parent_for_xml(tree, node['xml'])
        if node == None:
            break
    # Throw away the first chunk that always reads "Library"
    return " - ".join(full_name[1:])

def get_data(tree, node=None):
    def get_xml_from_api(url):
        xml_path = url.replace('https://directory.uchicago.edu', '')
        c = HTTPSConnection("directory.uchicago.edu")
        b = bytes(DIRECTORY_USERNAME + ':' + DIRECTORY_PASSWORD, 'utf-8')
        userAndPass = base64.b64encode(b).decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass } 
        c.request('GET', xml_path, headers=headers)
        result = c.getresponse()
    
        return ElementTree.fromstring(result.read())

    if node == None:
        node = tree

    x = get_xml_from_api(node['xml'])

    # no matter what, name is in the same place- but sometimes it gets split into chunks. 
    node['name'] = x.find(".//organizations/organization/name").text
   
    # division level 
    if node['xml'].find("/divisions/") > -1:
        for d in x.findall(".//departments/department/resources/xmlURL"):
            child_node = {
                'name': '',
                'xml': d.text,
                'children': []
            }
            node['children'].append(child_node)
            get_data(tree, child_node)

    # department level
    elif node['xml'].find("/departments/") > -1:
        parent_node = find_node_for_xml(tree, node['xml'])
        if not parent_node:
            parent_node = node
        for d in x.findall(".//subDepartments/subDepartment/resources/xmlURL"):
            child_node = {
                'name': '',
                'xml': d.text,
                'children': []
            }
            parent_node['children'].append(child_node)
            get_data(tree, child_node)

class Command (BaseCommand):
    """
    Report library units that are out of sync between Wagtail and the University Directory.

    Example: 
        python manage.py report_out_of_sync_library_units
    """

    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement this 
        method. It may return a Unicode string which will be printed to 
        stdout. More: https://docs.djangoproject.com/en/1.8/howto/custom
        -management-commands/#django.core.management.BaseCommand.handle
        """

        # GET A LIST OF THE DIRECTORY UNITS FROM THE UNIVERSITY'S API
        api_tree = {
            'xml': 'https://directory.uchicago.edu/api/v2/divisions/16',
            'name': '',
            'parent': None,
            'children': []
        }
        get_data(api_tree)

        # When node names contain pipes, split them and move them into place. 
        a = 0
        while a < len(api_tree['children']):
            b = 0
            while b < len(api_tree['children'][a]['children']):
                if '|' in api_tree['children'][a]['children'][b]['name']:
                    chunks = list(map(lambda s: s.strip(), api_tree['children'][a]['children'][b]['name'].split("|")))
                    p = 0
                    while p < len(api_tree['children'][a]['children']):
                        if api_tree['children'][a]['children'][p]['name'] == chunks[0]:
                            # e.g. "Law | Technical Services" becomes "Technical Services"
                            api_tree['children'][a]['children'][b]['name'] = chunks[1]
                            # e.g. copy "Technical Services" into the children of "Law".
                            api_tree['children'][a]['children'][p]['children'].append(api_tree['children'][a]['children'][b].copy())
                            # set name to the blank string. 
                            api_tree['children'][a]['children'][b]['name'] = ''
                        p = p + 1
                b = b + 1
            a = a + 1

        # Clean up after the routine above- remove the original "piped" nodes.
        a = 0
        while a < len(api_tree['children']):
            api_tree['children'][a]['children'] = list(filter(lambda c: c['name'], api_tree['children'][a]['children']))
            a = a + 1

        # sort everything alphabetically. 
        api_tree['children'] = sorted(api_tree['children'], key=lambda c: c['name'])
        a = 0
        while a < len(api_tree['children']):
            api_tree['children'][a]['children'] = sorted(api_tree['children'][a]['children'], key=lambda c: c['name'])
            b = 0
            while b < len(api_tree['children'][a]['children']):
                api_tree['children'][a]['children'][b]['children'] = sorted(api_tree['children'][a]['children'][b]['children'], key=lambda c: c['name'])
                b = b + 1
            a = a + 1

        # GET A LIST OF THE DIRECTORY UNITS IN WAGTAIL
        def get_children_of_unit(u):
            l = list(
                map(
                    lambda d: {
                        'name': d.name,
                        'xml': d.xmlUrl,
                        'children': []
                    }, list(DirectoryUnit.objects.filter(parentUnit=u))))
            return sorted(l, key=lambda c: c['name'])

        # first-level children:
        library_unit = DirectoryUnit.objects.get(xmlUrl='https://directory.uchicago.edu/api/v2/divisions/16')
        wagtail_tree = {
            'name': library_unit.name,
            'xml': library_unit.xmlUrl,
            'children': get_children_of_unit(library_unit)
        }

        # second-level children:
        a = 0
        while a < len(wagtail_tree['children']):
            wagtail_tree['children'][a]['children'] = get_children_of_unit(DirectoryUnit.objects.get(xmlUrl=wagtail_tree['children'][a]['xml']))
            # third-level children:
            b = 0
            while b < len(wagtail_tree['children'][a]['children']):
                wagtail_tree['children'][a]['children'][b]['children'] = get_children_of_unit(DirectoryUnit.objects.get(xmlUrl=wagtail_tree['children'][a]['children'][b]['xml']))
                b = b + 1
            a = a + 1

        # GET A REPORT ABOUT PLACES THE TREES ARE OUT OF SYNC
        # a and b are nodes from an api_tree or wagtail_tree
        def find_missing_units(a, b):
            a_set = set(map(lambda c: c['name'] + " " + c['xml'], a['children']))
            b_set = set(map(lambda c: c['name'] + " " + c['xml'], b['children']))

            output = []
            for d in b_set.difference(a_set):
                output.append(get_full_name_for_node(api_tree, b) + " - " + d.rsplit(' ', 1)[0])
            return output

        # api units, wagtail units
        au = []
        wu = []

        au = au + find_missing_units(api_tree, wagtail_tree)
        wu = wu + find_missing_units(wagtail_tree, api_tree)

        a = 0
        while a < len(api_tree['children']) and a < len(wagtail_tree['children']):
            au = au + find_missing_units(api_tree['children'][a], wagtail_tree['children'][a])
            wu = wu + find_missing_units(wagtail_tree['children'][a], api_tree['children'][a])
            b = 0
            while b < len(api_tree['children'][a]['children']) and b < len(wagtail_tree['children'][a]['children']):
                au = au + find_missing_units(api_tree['children'][a]['children'][b], wagtail_tree['children'][a]['children'][b])
                wu = wu + find_missing_units(wagtail_tree['children'][a]['children'][b], api_tree['children'][a]['children'][b])
                b = b + 1
            a = a + 1

        output = []
        if au:
            output.append("THE FOLLOWING UNITS APPEAR IN WAGTAIL, BUT NOT THE UNIVERSITY'S API:")
            output = output + sorted(au)
            output.append("")
        if wu:
            output.append("THE FOLLOWING UNITS APPEAR IN THE UNIVERSITY'S API, BUT NOT WAGTAIL:")
            output = output + sorted(wu)
            output.append("")

        # report DirectoryUnits that are not used in any IntranetUnitsPage. 
        # I commented this code out because we have a huge list of DirectoryUnits with no
        # associated page. There is no way to report this neatly, because of the number of 
        # DirectoryUnits that refer to a bibliographer's subject area, but not necessarily
        # a "unit" that should have reports, etc. 
        '''
        directory_unit_full_names = set(DirectoryUnit.objects.all().values_list('fullName', flat=True))
        intranetu_unit_full_names = set()
        for i in IntranetUnitsPage.objects.all():
            if i.unit:
                intranetu_unit_full_names.add(i.unit.fullName)

        output.append("ALL DIRECTORY UNIT FULL NAMES")
        output = output + sorted(list(directory_unit_full_names))
        output.append("")

        output.append("ALL INTRANET UNIT PAGE FULL NAMES")
        output = output + sorted(list(intranetu_unit_full_names))
        output.append("")

        diffs = directory_unit_full_names.difference(intranetu_unit_full_names)
        if diffs:
            output.append("THE FOLLOWING WAGTAIL DIRECTORY UNITS DO NOT HAVE INTRANETUNIT PAGES:")
            output = output + sorted(list(diffs)) + [""]
        '''

        return "\n".join(output)


