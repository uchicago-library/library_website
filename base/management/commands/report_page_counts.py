# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.apps import apps
from django.core.management.base import BaseCommand
from wagtail.core.models import Page

import sys

class Command (BaseCommand):
    """
    What does this do?

    Usage: 
        python manage.py report_page_counts
    """

    help = 'Get counts of all the objects in the system.'
     
    def handle(self, *args, **options):
        output = []
        for model in apps.get_models():
            output.append('{} {}.{}'.format(
                model.objects.all().count(),
                model.__module__,
                model.__name__
            ))
        return '\n'.join(output)
