from django.db import models
from django.db.models.fields import CharField, TextField
from django.utils import timezone
from staff.models import StaffPage
from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailcore.models import Page

class GroupPage(Page):
    """
    Content type for group and committee pages.
    """
    meeting_location = CharField(
        blank=True,
        max_length=255)
    meeting_time = models.TimeField(
        auto_now=False, 
        auto_now_add=False,
        default=timezone.now,
        blank=True) 
    description = models.TextField(null=True, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('description'),
        FieldPanel('meeting_time'),
    ]


class GroupIndexPage(Page):
    intro = TextField()

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ]

    subpage_types = ['group.GroupPage']
