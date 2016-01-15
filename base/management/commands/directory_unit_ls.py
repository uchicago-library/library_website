# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand

from directory_unit.models import DirectoryUnit
from intranetunits.models import IntranetUnitsPage
from staff.models import StaffPage, VCard

class Command (BaseCommand):
    """
    List information about a directory unit. 

    Example: 
        python manage.py directory_unit_ls
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

        # get the directory unit by it's full name
        directory_unit = DirectoryUnit.objects.get(fullName=kwargs['fullname'])

        # get the fullname, name, and xmlurl.
        output.append(directory_unit.fullName)
        output.append(directory_unit.name)
        output.append(directory_unit.xmlUrl)

        # get IntranetUnitsPages
        intranet_units_pages = list(IntranetUnitsPage.objects.filter(unit=directory_unit).values_list('url_path', flat=True))

        if intranet_units_pages:
            output.append("THE '" + kwargs['fullname'] + "' DirectoryUnit IS REFERENCED BY THE FOLLOWING INTRANETUNITSPAGE(S):")
            output = output + sorted(intranet_units_pages)

        # get a list of VCards and StaffPages
        staff_pages = []
        for v in VCard.objects.filter(unit=directory_unit):
            staff_pages = staff_pages + list(StaffPage.objects.filter(vcards=v).values_list('url_path', flat=True))

        if staff_pages:
            output.append("THE '" + kwargs['fullname'] + "' DirectoryUnit IS REFERENCED BY VCARDS BELONGING TO THE FOLLOWING STAFF MEMBER(S):")
            output = output + sorted(staff_pages)

        return "\n".join(output)


