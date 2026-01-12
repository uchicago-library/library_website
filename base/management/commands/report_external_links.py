# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import csv
import io

import django.apps
from django.core.management.base import BaseCommand
from django.db.models import URLField


class Command(BaseCommand):
    """
    Report external links from every page in the system.

    Example:
        python manage.py report_external_links
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
        writer.writerow(["Model", "Field", "Instance", "Value"])
        for model in django.apps.apps.get_models():
            for field in model._meta.fields:
                if isinstance(field, URLField):
                    for instance in model.objects.all():
                        try:
                            str_instance = instance.url_path
                        except:  # noqa: E722
                            str_instance = str(instance)
                        value = getattr(instance, field.name)
                        if not value:
                            value = ""
                        writer.writerow([str(model), field.name, str_instance, value])

        return output.getvalue()
