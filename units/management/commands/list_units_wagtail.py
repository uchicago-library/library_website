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

from units.utils import report_units_wagtail

class Command (BaseCommand):
    """
    Produce reports of units in Wagtail that can be imported into Excel. 
    """

    def add_arguments(self, parser):
        parser.add_argument('--all', action='store_true', default=False)
        parser.add_argument('--live', action='store_true', default=False)
        parser.add_argument('--latest_revision_created_at', type=str)
        parser.add_argument('--display_in_campus_directory', action='store_true', default=False)
        parser.add_argument('filename', type=str)

    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement this 
        method. It may return a Unicode string which will be printed to 
        stdout. More: https://docs.djangoproject.com/en/1.8/howto/custom
        -management-commands/#django.core.management.BaseCommand.handle
        """

        workbook = report_units_wagtail(**options)
        workbook.save(options['filename'])
