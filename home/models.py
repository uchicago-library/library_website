from __future__ import unicode_literals

from django.db import models

from wagtail.models import Page


class HomePage(Page):
    subpage_types = ['public.StandardPage', 'conferences.ConferenceIndexPage']
