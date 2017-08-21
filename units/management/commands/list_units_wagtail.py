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
    List units

    Example: 
        python manage.py list_units_wagtail --modified_since=20170501

        outputs full unit name (with names of ancestor units.) 
    """

    def add_arguments(self, parser):
        parser.add_argument('--all', action='store_true', default=False)
        parser.add_argument('--live', action='store_true', default=False)
        parser.add_argument('--modified_since', type=str)
        # add something for all units, even unpublished ones. 

    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement this 
        method. It may return a Unicode string which will be printed to 
        stdout. More: https://docs.djangoproject.com/en/1.8/howto/custom
        -management-commands/#django.core.management.BaseCommand.handle
        """

        if (len(sys.argv) < 3):
            print('Usage:')
            print('--all')
            print('--live')
            print('--modified_since yyyymmdd.')
            sys.exit()

        unit_ids = set()

        if options['all']:
            unit_ids = set(UnitPage.objects.all().values_list('id', flat=True))

        if options['live']:
            unit_ids = set(UnitPage.objects.live().values_list('id', flat=True))

        if options['modified_since']:
            modified_since_string = '{}-{}-{} 00:00-0600'.format(options['modified_since'][0:4],
                options['modified_since'][4:6], options['modified_since'][6:8])
            new_unit_ids = set(UnitPage.objects.filter(latest_revision_created_at__gte=modified_since_string).values_list('id', flat=True))
            unit_ids = unit_ids.intersection(new_unit_ids) if unit_ids else new_unit_ids

        output = []
        for unit in UnitPage.objects.filter(id__in=list(unit_ids)):
            try:
                latest_revision_created_at = unit.latest_revision_created_at.strftime('%m/%d/%Y %-I:%M:%S %p')
            except AttributeError:
                latest_revision_created_at = ''
                
            output.append('{}\t{}\t{}'.format(unit.id, latest_revision_created_at, unit.get_full_name()))

        return "\n".join(sorted(output))
