# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from base.utils import get_xml_from_directory_api
from django.core.management.base import BaseCommand
from staff.models import EMPLOYEE_TYPES, POSITION_STATUS, StaffPage, StaffPageLibraryUnits

import datetime
import pytz
import sys
import time

class Command (BaseCommand):
    """
    List staff

    Example: 
        python manage.py list_staff --cnetid=jej
        python manage.py list_staff --modified_since=20170501
        python manage.py list_staff --position_status=active|vacant|eliminated
        python manage.py list_staff --supervises_students
        python manage.py list_staff --supervisor_cnetid=chas
        python manage.py list_staff --title=manager

        outputs cnetid, name (of previous staff member?), title, phone, email,
            faculty_exchange, department (full name), employee_type, supervises_students,
            supervisor_cnetid.
                is department full name the unit?
    """

    def add_arguments(self, parser):
        cnetids = sorted(StaffPage.objects.all().values_list('cnetid', flat=True))
        parser.add_argument('--all', action='store_true', default=False)
        parser.add_argument('--cnetid', type=str, choices=cnetids)
        parser.add_argument('--department', type=str)
        parser.add_argument('--live', action='store_true', default=False)
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
            print('--all: list every staff person.')
            print('--cnetid abc')
            print('--department title')
            print('--live: current staff only.')
            print('--modified_since yyyymmdd.')
            print('-position_status: Exempt, etc.')
            print('--supervises_students: true or false.')
            print('--supervisor_cnetid abc.')
            print('--supervisor_override_set.')
            print('--title')
            sys.exit()

        cnetids = set()

        if options['all']:
            cnetids = set(StaffPage.objects.all().values_list('cnetid', flat=True))
        elif options['live']:
            cnetids = set(StaffPage.objects.live().values_list('cnetid', flat=True))
        else:
	        if options['cnetid']:
	            cnetids = set([options['cnetid']])
	
	        if options['department']:
	            new_cnetids = list(StaffPageLibraryUnits.objects.filter(library_unit__title=options['department']).values_list('page__cnetid', flat=True))
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
       
        # JEJ get the stuff it outputs.  
        for cnetid in cnetids:
            s = StaffPage.objects.get(cnetid=cnetid)
            units = StaffPageLibraryUnits.objects.filter(page__cnetid=cnetid)
            units_string = ''
            if units:
                units_string = '|'.join(units.values_list('library_unit__title', flat=True))

            supervisor_cnetids = ''
            if s.supervisor_override:
                supervisor_cnetids = s.supervisor_override.cnetid
            elif units:
                try:
                    supervisor_cnetids = '|'.join(units.values_list('library_unit__department_head__cnetid', flat=True))
                except TypeError:
                    pass

   
            employee_type_string = [v for i, v in EMPLOYEE_TYPES if i == s.employee_type][0]
            position_status_string = [v for i, v in POSITION_STATUS if i == s.position_status][0]
                
            fields = [
                cnetid,
                s.title or '',
                s.position_title or '',
                s.phone_number or '',
                s.email or '',
                s.faculty_exchange or '',
                units_string,
                employee_type_string,
                str(s.supervises_students),
                position_status_string,
                supervisor_cnetids
            ]

            print("\t".join(fields))
        '''
        try:
        except:
            sys.exit(1)
        '''

    


