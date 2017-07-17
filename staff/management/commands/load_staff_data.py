# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from base.utils import get_xml_from_directory_api
from django.core.management.base import BaseCommand
from staff.models import EMPLOYEE_TYPES, StaffPage, StaffPageLibraryUnits
from staff.utils import get_all_library_cnetids_from_directory, get_individual_info_from_directory
from units.models import UnitPage

import csv

#import os
#os.environ['DJANGO_SETTINGS_MODULE'] = 'library_website.settings'

class Command (BaseCommand):
    """
    Report staff member data that is out of sync between the University directory and Wagtail.

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

        output = []

        StaffPageLibraryUnits.objects.all().delete()

        employee_type_dict = {}
        for i, v in EMPLOYEE_TYPES:
            employee_type_dict[v] = i

        with open('staff-data.csv', newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in spamreader:
                if row[0] == 'cnetid':
                    continue
                
                s = StaffPage.objects.get(cnetid=row[0])

                s.position_title = row[2]
                s.phone_number = row[3]
                s.email = row[4]
                s.faculty_exchange = row[5]
                StaffPageLibraryUnits.objects.create(library_unit=UnitPage.objects.get(title=row[6]), page=s)
                s.employee_type = employee_type_dict[row[7]]
                s.supervises_students = True if row[8] == 'TRUE' else False
                s.save()

        unit_heads = [
            ("Administration", "brendajohnson"),
            ("Administration - Communications", "rrosenbe"),
            ("Administration - Development", "yasminomer"),
            ("Administration - Director's Office", "brendajohnson"),
            ("Administrative Services", "sbabcock"),
            ("Administrative Services - Budget", "dnborycz"),
            ("Administrative Services - Building Services", "jjcarey"),
            ("Administrative Services - Human Resources", "sbabcock"),
            ("Administrative Services - Shipping and Receiving", "jjcarey"),
            ("Area Studies, Humanities, and Social Sciences", "plb4"),
            ("Collection Services - Administrative and Desktop Systems (ADS)", "dfarley"),
            ("Collection Services - Integrated Library Systems (ILS)", "tod"),
            ("Collection Services - Preservation", "kar8"),
            ("Collection Services - Preservation - Conservation", "annlindsey"),
            ("Digital Services", "elong"),
            ("Digital Services - Digital Library Development Center (DLDC)", "chas"),
            ("Science Libraries", "bkern"),
            ("Special Collections Research Center", "arch")
        ]

        for u in unit_heads:
            unit_page = UnitPage.objects.get(title=u[0])
            unit_page.department_head = StaffPage.objects.get(cnetid=u[1])
            unit_page.page_maintainer = StaffPage.objects.get(cnetid='dbietila')
            unit_page.editor = StaffPage.objects.get(cnetid='dbietila')
            unit_page.save()

        return "\n".join(output)


