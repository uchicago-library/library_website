# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand

from base.utils import get_xml_from_directory_api
from units.models import UnitPage
from xml.etree import ElementTree

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

        api_units = set()
        x = ElementTree.fromstring(get_xml_from_directory_api('https://directory.uchicago.edu/api/v2/divisions/16'))
        for d in x.findall(".//departments/department"):
            department_name = d.find('name').text
            department_xml = d.find('resources/xmlURL').text
            x2 = ElementTree.fromstring(get_xml_from_directory_api(department_xml))
            for d2 in x2.findall(".//subDepartments/subDepartment"):
                subdepartment_name = d2.find('name').text
                api_units.add(department_name + ' - ' + subdepartment_name)

        wag_units = set()
        for unit_page in UnitPage.objects.live().filter(display_in_campus_directory=True):
            wag_units.add(unit_page.get_full_name())

        au = sorted(list(api_units.difference(wag_units)))
        wu = sorted(list(wag_units.difference(api_units)))

        output = []
        if au:
            output.append("THE FOLLOWING UNITS APPEAR IN WAGTAIL, BUT NOT THE UNIVERSITY'S API:")
            output = output + wu
            output.append("")
        if wu:
            output.append("THE FOLLOWING UNITS APPEAR IN THE UNIVERSITY'S API, BUT NOT WAGTAIL:")
            output = output + au
            output.append("")

        return "\n".join(output)


