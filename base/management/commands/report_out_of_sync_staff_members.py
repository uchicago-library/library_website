# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand

#import os
#os.environ['DJANGO_SETTINGS_MODULE'] = 'library_website.settings'

from staff.utils import get_all_library_cnetids_from_directory, get_all_library_cnetids_from_wagtail, get_individual_info_from_directory, get_individual_info_from_wagtail

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

        '''
        # JEJ
        print(
        get_individual_info_from_directory('amybuckland')
        )
        import sys
        sys.exit()
        '''

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
    


