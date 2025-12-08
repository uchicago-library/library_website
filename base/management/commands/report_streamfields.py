# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import csv
import io

import django.apps
from django.core.management.base import BaseCommand
from wagtail.fields import StreamField


class Command(BaseCommand):
    """
    Get streamfields from every page.

    Example:
        python manage.py report_streamfields
    """

    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement this
        method. It may return a Unicode string which will be printed to
        stdout. More: https://docs.djangoproject.com/en/1.8/howto/custom
        -management-commands/#django.core.management.BaseCommand.handle
        """

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["URL", "Value"])
        for model in django.apps.apps.get_models():
            for field in model._meta.fields:
                if isinstance(field, StreamField):
                    for instance in model.objects.all():
                        try:
                            value = str(getattr(instance, str(field).split(".").pop()))
                        except AttributeError:
                            continue
                        if not value:
                            value = ""
                        if "motacilla.lib.uchicago.edu" in value:
                            writer.writerow([instance.url, value])

        return output.getvalue()
