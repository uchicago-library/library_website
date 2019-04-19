# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from units.models import UnitPage

class Command (BaseCommand):
    def handle(self, *args, **options):
        # assume that if the department head of a unit has an unpublished staff page,
        # that the staff person has left the library.
        units_with_unpublished_department_heads = UnitPage.objects.exclude(department_head=None).filter(department_head__live=False)
        if units_with_unpublished_department_heads:
            print('The following UnitPages have a department_head with an unpublished StaffPage.')
            print('')
            for u in units_with_unpublished_department_heads:
                print(u.url_path)
                print(u.department_head.title)
                print('') 
