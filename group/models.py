from django.db import models
from django.db.models.fields import CharField, TextField
from django.utils import timezone
from datetime import datetime, timedelta

from base.models import DefaultBodyFields, Email, Report
from base.models import BasePage
from staff.models import StaffPage
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel, StreamFieldPanel
from wagtail.wagtailcore.models import Orderable, Page
from modelcluster.fields import ParentalKey
from wagtail.wagtailsearch import index
from wagtail.wagtailsnippets.models import register_snippet

from wagtail.wagtaildocs.models import Document
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel

def default_end_time():
    """
    Callback function for setting the default
    meeting end time.
    """
    return datetime.now() + timedelta(hours=1)


@register_snippet
class GroupMemberRole(models.Model, index.Indexed):
    """
    Snippet for group member roles.
    """
    text = models.CharField(max_length=255, blank=False)

    panels = [
        FieldPanel('text'),
    ]

    def __str__(self):
        return self.text

    search_fields = [
        index.SearchField('text', partial_match=True),
    ]


class MeetingMinutes(models.Model):
    """
    Meeting minutes content type.
    """
    date = models.DateField(blank=False)
    summary = models.TextField(null=False, blank=False)
    link = models.URLField(max_length=254, blank=True, default='')
    document = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    ) 

    panels = [
        FieldPanel('date'),
        FieldPanel('summary'),
        DocumentChooserPanel('document'),
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
    role = models.ForeignKey(
        'group.GroupMemberRole', 
        null=True,
        blank=True,
        related_name='+'
    )    

    class Meta:
        verbose_name = 'Member'
        verbose_name_plural = 'Members'

class GroupPage(BasePage, Email):
    """
    Content type for group and committee pages.
    """
    meeting_location = CharField(
        blank=True,
        max_length=255)
    meeting_start_time = models.TimeField(
        auto_now=False, 
        auto_now_add=False,
        default=timezone.now,
        blank=True)
    meeting_end_time = models.TimeField(
        auto_now=False, 
        auto_now_add=False,
        default=default_end_time,
        blank=True) 
    meeting_frequency = CharField(
        blank=True,
        max_length=255)
    intro = StreamField(DefaultBodyFields(), blank=True)
    is_active = models.BooleanField(default=False)
    body = StreamField(DefaultBodyFields())


    content_panels = Page.content_panels + Email.content_panels + [
        MultiFieldPanel(
            [
               FieldPanel('meeting_start_time'),
               FieldPanel('meeting_end_time'),              
               FieldPanel('meeting_location'), 
               FieldPanel('meeting_frequency'),
            ],
            heading='Meeting Information'
        ),
        StreamFieldPanel('intro'),
        InlinePanel('meeting_minutes', label='Meeting Minutes'),
        InlinePanel('group_reports', label='Reports'),
        InlinePanel('group_members', label='Group Members'),
        FieldPanel('is_active'),
        StreamFieldPanel('body'),
    ] + BasePage.content_panels 

    def get_context(self, request):
        context = super(GroupPage, self).get_context(request)

        group_members = self.group_members.all()

        # sorting: chairs or co-chairs first, alphabetically; then others, alphabetically. 
        group_member_chairs = []
        non_group_member_chairs = []
        for g in group_members:
            if g.role and g.role.text in ['Chair', 'Co-Chair']:
                group_member_chairs.append(g)
            else:
                non_group_member_chairs.append(g)
        group_member_chairs = sorted(group_member_chairs, key=lambda g: g.group_member.title)
        non_group_member_chairs = sorted(non_group_member_chairs, key=lambda g: g.group_member.title)

        group_members = group_member_chairs + non_group_member_chairs

        context['group_members'] = list(map(lambda m: { 'title': m.group_member.title, 'unit': '<br/>'.join(sorted(map(lambda u: u.unit.fullName, m.group_member.vcards.all()))), 'url': m.group_member.url, 'role': m.role }, group_members))
        return context

class GroupIndexPage(BasePage):
    intro = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ] + BasePage.content_panels

    subpage_types = ['base.IntranetPlainPage', 'group.GroupPage']

    def get_context(self, request):
        context = super(GroupIndexPage, self).get_context(request)
        context['groups_active'] = list(map(lambda g: { 'title': g.title, 'url': g.url }, GroupPage.objects.live().filter(is_active=True).order_by('title')))
        context['groups_inactive'] = list(map(lambda g: { 'title': g.title, 'url': g.url }, GroupPage.objects.live().filter(is_active=False).order_by('title')))
        return context
