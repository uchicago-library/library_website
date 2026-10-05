from __future__ import unicode_literals

from wagtail.models import Page


class HomePage(Page):
    subpage_types = ["public.StandardPage", "conferences.ConferenceIndexPage"]
