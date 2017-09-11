# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand

from units.utils import units_out_of_sync


class Command (BaseCommand):
    """
    Report library units that are out of sync between Wagtail and the
    University Directory.

    Example:
        python manage.py report_out_of_sync_library_units
    """

    def handle(self, *args, **options):
        cu, wu = units_out_of_sync()
        output = []
        if wu:
            output.append("THE FOLLOWING UNITS APPEAR IN WAGTAIL, BUT NOT THE UNIVERSITY'S API:")
            output = output + wu
            output.append("")
        if cu:
            output.append("THE FOLLOWING UNITS APPEAR IN THE UNIVERSITY'S API, BUT NOT WAGTAIL:")
            output = output + cu
            output.append("")
        return "\n".join(output)
