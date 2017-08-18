# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from base.utils import get_xml_from_directory_api
from django.core.management.base import BaseCommand
from staff.models import EMPLOYEE_TYPES, POSITION_STATUS, StaffPage, StaffPageLibraryUnits
from units.models import UnitPage

import datetime
import pytz
import sys
import time

class Command (BaseCommand):
    """
    List staff

    Example: 
        python manage.py list_staff_wagtail --cnetid=jej
        python manage.py list_staff_wagtail --modified_since=20170501
        python manage.py list_staff_wagtail --position_status=active|vacant|eliminated
        python manage.py list_staff_wagtail --supervises_students
        python manage.py list_staff_wagtail --supervisor_cnetid=chas
        python manage.py list_staff_wagtail --title=manager

        outputs cnetid, name (of previous staff member?), title, phone, email,
            faculty_exchange, department (full name), employee_type, supervises_students,
            supervisor_cnetid.
                is department full name the unit?
    """

    def add_arguments(self, parser):
        cnetids = sorted(StaffPage.objects.all().values_list('cnetid', flat=True))
        parser.add_argument('--cnetid', type=str, choices=cnetids)
        parser.add_argument('--department', type=str)
        parser.add_argument('--department_and_subdepartments', type=str)
        parser.add_argument('--include_unpublished', action='store_true', default=False)
        parser.add_argument('--modified_since', type=str)
        parser.add_argument('--position_status', type=str, choices=[status[1] for status in POSITION_STATUS])
        parser.add_argument('--supervises_students', action='store_true', default=False)
        parser.add_argument('--supervisor_cnetid', type=str, choices=cnetids)
        parser.add_argument('--supervisor_override_set', action='store_true', default=False)
        parser.add_argument('--title', type=str)

    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement this 
        method. It may return a Unicode string which will be printed to 
        stdout. More: https://docs.djangoproject.com/en/1.8/howto/custom
        -management-commands/#django.core.management.BaseCommand.handle
        """

        if (len(sys.argv) < 3):
            print('Usage:')
            print('--cnetid abc')
            print('--department title')
            print('--department_and_subdepartments title')
            print('--include_unpublished: search all StaffPage objects, not just live pages.')
            print('--modified_since yyyymmdd.')
            print('-position_status: Exempt, etc.')
            print('--supervises_students: true or false.')
            print('--supervisor_cnetid abc.')
            print('--supervisor_override_set.')
            print('--title')
            sys.exit()

        cnetids = set()

        if options['include_unpublished']:
            cnetids = set(StaffPage.objects.all().values_list('cnetid', flat=True))
        else:
            if options['cnetid']:
                cnetids = set([options['cnetid']])
            else:
                cnetids = set(StaffPage.objects.live().values_list('cnetid', flat=True))
    
            if options['department']:
                new_cnetids = list(StaffPageLibraryUnits.objects.filter(library_unit__title=options['department']).values_list('page__cnetid', flat=True))
                cnetids = cnetids.intersection(new_cnetids) if cnetids else set(new_cnetids)

            if options['department_and_subdepartments']:
                unit_pages = UnitPage.objects.descendant_of(UnitPage.objects.get(title=options['department_and_subdepartments']), True)
                new_cnetids = list(StaffPageLibraryUnits.objects.filter(library_unit__in=unit_pages).values_list('page__cnetid', flat=True))
                cnetids = cnetids.intersection(new_cnetids) if cnetids else set(new_cnetids)
    
            if options['modified_since']:
                modified_since_string = '{}-{}-{} 00:00-0600'.format(options['modified_since'][0:4],
                    options['modified_since'][4:6], options['modified_since'][6:8])
                new_cnetids = list(StaffPage.objects.filter(latest_revision_created_at__gte=modified_since_string).values_list('cnetid', flat=True))
                cnetids = cnetids.intersection(new_cnetids) if cnetids else set(new_cnetids)
    
            if options['position_status']:
                position_status_int = [i for i, v in POSITION_STATUS if v == options['position_status']][0]
                new_cnetids = list(StaffPage.objects.filter(position_status=position_status_int).values_list('cnetid', flat=True))
                cnetids = cnetids.intersection(new_cnetids) if cnetids else set(new_cnetids)
    
            if options['supervises_students']:
                new_cnetids = list(StaffPage.objects.filter(supervises_students=True).values_list('cnetid', flat=True))
                cnetids = cnetids.intersection(new_cnetids) if cnetids else set(new_cnetids)
    
            if options['supervisor_cnetid']:
                new_cnetids = list(StaffPage.objects.get(cnetid=options['supervisor_cnetid']).get_staff().values_list('cnetid', flat=True))
                cnetids = cnetids.intersection(new_cnetids) if cnetids else set(new_cnetids)
    
            if options['supervisor_override_set']:
                new_cnetids = list(StaffPage.objects.exclude(supervisor_override=None).values_list('cnetid', flat=True))
                cnetids = cnetids.intersection(new_cnetids) if cnetids else set(new_cnetids)
    
            if options['title']:
                new_cnetids = list(StaffPage.objects.filter(position_title=options['title']).values_list('cnetid', flat=True))
                cnetids = cnetids.intersection(new_cnetids) if cnetids else set(new_cnetids)

        # sort by last name
        cnetids = StaffPage.objects.filter(cnetid__in=cnetids).order_by('last_name').values_list('cnetid', flat=True)
      
        output = [] 

        for cnetid in cnetids:
            units = StaffPageLibraryUnits.objects.filter(page__cnetid=cnetid).values_list('library_unit__title', flat=True)

            s = StaffPage.objects.get(cnetid=cnetid)

            name_and_cnetid = '%s (%s)' % (s.title, cnetid)

            supervisor_names_and_cnetids = ['%s (%s)' % (s.title, s.cnetid) for s in s.get_supervisors]

            emails = [e.email for e in s.staff_page_email.all()]

            phone_facexes = ['%s,%s' % (p.faculty_exchange, p.phone_number) for p in s.staff_page_phone_faculty_exchange.all()]

            employee_type_string = [v for i, v in EMPLOYEE_TYPES if i == s.employee_type][0]

            position_status_string = [v for i, v in POSITION_STATUS if i == s.position_status][0]

            fields = [
                name_and_cnetid,
                s.position_title or '',
                '|'.join(emails) or '',
                '|'.join(phone_facexes) or '',
                '|'.join(units) or '',
                employee_type_string,
                str(s.supervises_students),
                position_status_string,
                '|'.join(supervisor_names_and_cnetids)
            ]
            output.append("\t".join(fields))

        return "\n".join(output)

    


