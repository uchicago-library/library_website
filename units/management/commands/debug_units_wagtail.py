# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand

from intranetunits.models import IntranetUnitsPage
from staff.models import StaffPage
from units.models import UnitPage

class Command (BaseCommand):
    """
    List information about an intranet unit page.

    Example: 
        python manage.py list_intranetunits_wagtail
    """

    def add_arguments(self, parser):
        """
        Add required positional options and optional
        named arguments.
        """
        # Required positional options
        parser.add_argument('fullname', type=str)

    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement this 
        method. It may return a Unicode string which will be printed to 
        stdout. More: https://docs.djangoproject.com/en/1.8/howto/custom
        -management-commands/#django.core.management.BaseCommand.handle
        """

        # Convenience variables for required fields.
        # Save in a dict so we can pass an unspecified
        # numer or arguments to the get_or_create method.
        try:
            kwargs = { 'fullname': options['fullname'] }
        except:
            sys.exit(1)

        output = []

        unit_page = None
        for u in UnitPage.objects.live():
            if u.get_full_name() == kwargs['fullname']:
                unit_page = u

        if unit_page:
            output.append(unit_page.get_full_name())

            intranet_units_pages = list(IntranetUnitsPage.objects.filter(unit_page=unit_page).values_list('url_path', flat=True))

            if intranet_units_pages:
                output.append("THE '" + kwargs['fullname'] + "' UnitPage IS REFERENCED BY THE FOLLOWING INTRANETUNITSPAGE(S):")
                output = output + sorted(intranet_units_pages)

        return "\n".join(output)


