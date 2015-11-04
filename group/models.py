from django.db import models
from django.db.models.fields import CharField, TextField
from django.utils import timezone
from staff.models import StaffPage
from base.models import DefaultBodyFields, Email, Report
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel, StreamFieldPanel
from wagtail.wagtailcore.models import Orderable, Page
from modelcluster.fields import ParentalKey

class MeetingMinutes(models.Model):
    """
    Meeting minutes content type.
    """
    date = models.DateField(blank=False)
    summary = models.TextField(null=False, blank=False)
    link = models.URLField(max_length=254, blank=False, default='')

    panels = [
        FieldPanel('date'),
        FieldPanel('summary'),
        FieldPanel('link'),
    ]

    class Meta:
        abstract = True


class GroupPageMeetingMinutes(Orderable, MeetingMinutes):
    """
    Meeting minutes for group pages.
    """
    page = ParentalKey('group.GroupPage', related_name='meeting_minutes')


class GroupPageReports(Orderable, Report):
    """
    Reports for group pages.
    """
    page = ParentalKey('group.GroupPage', related_name='group_reports')


class GroupPage(Page, Email):
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
    meeting_frequency = CharField(
        blank=True,
        max_length=255)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    body = StreamField(DefaultBodyFields())


    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
               FieldPanel('meeting_time'),
               FieldPanel('meeting_location'), 
               FieldPanel('meeting_frequency'),
            ],
            heading='Meeting Information'
        ),
        FieldPanel('description'),
        InlinePanel('meeting_minutes', label='Meeting Minutes'),
        InlinePanel('group_reports', label='Reports'),
        FieldPanel('is_active'),
        StreamFieldPanel('body'),
    ] + Email.content_panels


class GroupIndexPage(Page):
    intro = TextField()

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ]

    subpage_types = ['group.GroupPage']
