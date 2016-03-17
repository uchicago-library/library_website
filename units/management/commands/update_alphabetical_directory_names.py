# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from units.models import UnitPage

class Command (BaseCommand):
    """
    Update the alphabetical directory names: e.g.
    Administration, D'Angelo Law Library.

    Example: 
        python manage.py update_alphabetical_directory_names
    """

    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement this 
        method. It may return a Unicode string which will be printed to 
        stdout. More: https://docs.djangoproject.com/en/1.8/howto/custom
        -management-commands/#django.core.management.BaseCommand.handle
        """

        output = []

        def get_shortest_unique_breadcrumb_trail(trails, trail):
            checking_trails = trails
            column = 0
            while True:
                # just in case.
                if column > 10:
                    raise RuntimeError
                checking_trails = list(filter(lambda t, trail = trail, column = column: t[0:column] == trail[0:column], checking_trails)) 
                if len(checking_trails) == 1:
                    return ', '.join(checking_trails[0][0:column])
                column = column + 1
            # just in case. 
            raise RuntimeError

        breadcrumb_trails = []
        for u in UnitPage.objects.filter(display_in_directory=True):
            breadcrumb_trails.append(list(reversed(u.get_full_name().split(' - '))))

        units_updated = 0
        for u in UnitPage.objects.filter(display_in_directory=True):
            breadcrumb_trail = list(reversed(u.get_full_name().split(' - ')))
            breadcrumb_string = get_shortest_unique_breadcrumb_trail(breadcrumb_trails, breadcrumb_trail)
            if not u.alphabetical_directory_name == breadcrumb_string:
                u.alphabetical_directory_name = breadcrumb_string
                u.save()
                units_updated = units_updated + 1

        output.append(str(units_updated) + " units updated.")

        return "\n".join(output)
    


