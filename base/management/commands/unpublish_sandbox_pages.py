# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from wagtail.models import Page


class Command(BaseCommand):
    """
    Unpublish sandbox pages.

    Example:
        python manage.py unpublish_sandbox_pages
    """

    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement this
        method. It may return a Unicode string which will be printed to
        stdout. More: https://docs.djangoproject.com/en/1.8/howto/custom
        -management-commands/#django.core.management.BaseCommand.handle
        """

        output = ""
        try:
            for p in Page.objects.get(title="Sandbox").get_descendants():
                p.unpublish()
        except Exception as e:
            output = str(e)

        return output
