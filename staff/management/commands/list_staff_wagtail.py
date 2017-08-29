# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from staff.models import POSITION_STATUS, StaffPage
from staff.utils import report_staff_wagtail

class Command (BaseCommand):
    """
    Produce reports of staff in Wagtail that can be imported into Excel. 
    """

    def add_arguments(self, parser):
        cnetids = sorted(StaffPage.objects.all().values_list('cnetid', flat=True))
        parser.add_argument('--all', default=False, action='store_true', dest='all')
        parser.add_argument('--cnetid', type=str, action='store', choices=cnetids, dest='cnetid')
        parser.add_argument('--department', type=str, action='store', dest='department')
        parser.add_argument('--department_and_subdepartments', type=str, action='store', dest='department_and_subdepartments')
        parser.add_argument('--live', default=False, action='store_true', dest='live')
        parser.add_argument('--latest_revision_created_at', type=str, action='store', dest='latest_revision_created_at')
        parser.add_argument('--position_status', type=str, action='store', choices=[status[1] for status in POSITION_STATUS], dest='position_status')
        parser.add_argument('--supervises_students', default=False, action='store_true', dest='supervises_students')
        parser.add_argument('--supervisor_cnetid', type=str, action='store', choices=cnetids, dest='supervisor_cnetid')
        parser.add_argument('--supervisor_override', default=False, action='store_true', dest='supervisor_override')
        parser.add_argument('--position_title', type=str, action='store', dest='position_title')
        parser.add_argument('filename', type=str)

    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement this 
        method. It may return a Unicode string which will be printed to 
        stdout. More: https://docs.djangoproject.com/en/1.8/howto/custom
        -management-commands/#django.core.management.BaseCommand.handle
        """

        workbook = report_staff_wagtail(**options)
        workbook.save(options['filename'])
        return ''

    


