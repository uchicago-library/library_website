# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import urllib.request

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Retrieve pages over http to refresh the template fragment cache.

    Usage:
        python manage.py refresh_template_fragment_cache
    """

    def handle(self, *args, **options):
        urls = [
            "https://www.lib.uchicago.edu/about/directory/?view=staff",
            "https://www.lib.uchicago.edu/about/directory/?view=department",
        ]

        for url in urls:
            urllib.request.urlopen(url)
