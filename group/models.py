from django.db import models
from django.db.models.fields import CharField, TextField
from django.utils import timezone

from base.models import DefaultBodyFields, Email, Report
from staff.models import StaffPage
from wagtail.wagtailcore.fields import RichTextField, StreamField
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


class GroupMembers(Orderable, models.Model):
    """
    Through table for linking staff pages to 
    groups and committees.
    """
    parent = ParentalKey(
        'group.GroupPage',
        related_name='group_members',
        null=True,
        blank=False,
        on_delete=models.SET_NULL
    )

    group_member = models.ForeignKey(
        'staff.StaffPage',
        related_name='member',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    class Meta:
        verbose_name = 'Member'
        verbose_name_plural = 'Members'

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


    content_panels = Page.content_panels + Email.content_panels + [
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
        InlinePanel('group_members', label='Group Members'),
        FieldPanel('is_active'),
        StreamFieldPanel('body'),
    ] 

class GroupIndexPage(Page):
    intro = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ]

    subpage_types = ['group.GroupPage']
