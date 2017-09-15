# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand

from units.utils import WagtailUnitsReport


class Command (BaseCommand):
    """
    Report library units that are out of sync between Wagtail and the
    University Directory.

    Example:
        python manage.py report_out_of_sync_library_units
    """

    def handle(self, *args, **options):
        units_report = WagtailUnitsReport(
            sync_report = True,
            unit_report = False,
            all = False,
            display_in_campus_directory = False,
            latest_revision_created_at = None,
            live = True
        )

        return units_report.tab_delimited()
