# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from base.utils import get_xml_from_directory_api
from staff.utils import get_all_library_cnetids_from_directory, get_individual_info_from_directory
from django.core.management.base import BaseCommand

import sys

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

        cnetids = get_all_library_cnetids_from_directory() 
        for cnetid in cnetids:
            xml_string = get_xml_from_directory_api('https://directory.uchicago.edu/api/v2/individuals/' + cnetid + '.xml')
            info = get_individual_info_from_directory(xml_string)

            try:
                displayname = info['displayName']
            except:
                displayname = ''

            try:
                title = info['title_department_subdepartments_dicts'][0]['title']
            except:
                title = ''

            try:
                phone = info['title_department_subdepartments_dicts'][0]['phone']
            except:
                phone = ''

            try:
                email = info['title_department_subdepartments_dicts'][0]['email']
            except:
                email = ''

            try:
                facultyexchange = info['title_department_subdepartments_dicts'][0]['facultyexchange']
            except:
                facultyexchange = ''

            fields = [
                cnetid,
                displayname,
                title,
                phone,
                email,
                facultyexchange,
            ]
            output.append("\t".join(fields)) 

        return "\n".join(output)
    


