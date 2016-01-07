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
        ordering = ['-date']


class GroupMeetingMinutesPageTable(Orderable, MeetingMinutes):
    """
    Meeting minutes for group pages.
    """
    page = ParentalKey('group.GroupMeetingMinutesPage', related_name='meeting_minutes')


class GroupReportsPageTable(Orderable, Report):
    """
    Reports for group pages.
    """
    page = ParentalKey('group.GroupReportsPage', related_name='group_reports')


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
        blank=True,
        null=True)
    meeting_end_time = models.TimeField(
        auto_now=False, 
        auto_now_add=False,
        default=default_end_time,
        blank=True,
        null=True) 
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
        InlinePanel('group_members', label='Group Members'),
        FieldPanel('is_active'),
        StreamFieldPanel('body'),
    ] + BasePage.content_panels 

    subpage_types = ['base.IntranetIndexPage', 'base.IntranetPlainPage', 'group.GroupPage', 'group.GroupMeetingMinutesPage', 'group.GroupReportsPage']

    def get_context(self, request):
        context = super(GroupPage, self).get_context(request)

        group_members = self.group_members.all()

        # sorting: chairs or co-chairs first, alphabetically; then others, alphabetically. 
        group_member_chairs = []
        non_group_member_chairs = []
        for g in group_members:
            if g.group_member == None:
                continue
            if g.role and g.role.text in ['Chair', 'Co-Chair']:
                group_member_chairs.append(g)
            else:
                non_group_member_chairs.append(g)

        group_member_chairs = sorted(group_member_chairs, key=lambda g: g.group_member.title)
        non_group_member_chairs = sorted(non_group_member_chairs, key=lambda g: g.group_member.title)
        group_members = group_member_chairs + non_group_member_chairs

        # minutes
        minutes = []
        group_meeting_min_page = GroupMeetingMinutesPage.objects.descendant_of(self).first()
        if group_meeting_min_page:
            for m in group_meeting_min_page.meeting_minutes.order_by('-date')[:3]:
                try:
                    if not m.link and not m.document.url:
                        continue
                except AttributeError:
                    continue
                minute = {
                    'summary': m.summary,
                    'date': m.date.strftime("%b. %-d, %Y")
                }
                if m.link:
                    minute['url'] = m.link
                elif m.document.url:
                    minute['url'] = m.document.url
                minutes.append(minute)

        #reports
        reports = []
        group_reports_page = GroupReportsPage.objects.descendant_of(self).first()
        if group_reports_page:
            for r in group_reports_page.group_reports.order_by('-date')[:3]:
                if not r.link and not r.document.url:
                    continue
                report = {
                    'summary': r.summary,
                    'date': r.date.strftime("%b. %-d, %Y")
                }
                if r.link:
                    report['url'] = r.link
                elif r.document.url:
                    report['url'] = r.document.url
                reports.append(report)

        context['minutes'] = minutes
        context['reports'] = reports
        context['group_members'] = list(map(lambda m: { 'title': m.group_member.title, 'unit': '<br/>'.join(sorted(map(lambda u: u.unit.fullName, m.group_member.vcards.all()))), 'url': m.group_member.url, 'role': m.role }, group_members))
        return context

class GroupMeetingMinutesPage(BasePage):
    content_panels = Page.content_panels + [
        InlinePanel('meeting_minutes', label='Meeting Minutes'),
    ] + BasePage.content_panels 

    subpage_types = []

    def get_context(self, request):
        context = super(GroupMeetingMinutesPage, self).get_context(request)

        minutes = []
        for m in self.meeting_minutes.order_by('-date'):
            if not m.link and not m.document.url:
                continue
            minute = {
                'summary': m.summary,
                'date': m.date.strftime("%b. %-d, %Y")
            }
            if m.link:
                minute['url'] = m.link
            elif m.document.url:
                minute['url'] = m.document.url
            minutes.append(minute)

        context['minutes'] = minutes
        return context

class GroupReportsPage(BasePage):
    content_panels = Page.content_panels + [
        InlinePanel('group_reports', label='Reports'),
    ] + BasePage.content_panels 

    subpage_types = []

    def get_context(self, request):
        context = super(GroupReportsPage, self).get_context(request)

        reports = []
        for r in self.group_reports.order_by('-date'):
            if not r.link and not r.document.url:
                continue
            report = {
                'summary': r.summary,
                'date': r.date.strftime("%b. %-d, %Y")
            }
            if r.link:
                report['url'] = r.link
            elif r.document.url:
                report['url'] = r.document.url
            reports.append(report)

        context['reports'] = reports
        return context

class GroupIndexPage(BasePage):
    intro = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ] + BasePage.content_panels

    subpage_types = ['base.IntranetIndexPage', 'base.IntranetPlainPage', 'group.GroupPage']

    def get_context(self, request):
        context = super(GroupIndexPage, self).get_context(request)

        groups_active = [{
            'title': GroupIndexPage.objects.first().title,
            'url': GroupIndexPage.objects.first().url,
            'children': [],
        }]

        # for each group page get a list of the page's "group page" or "group
        # index page" ancestors. Check to see if this particular ancestor
        # already exists in the groups_active tree. If it doesn't exist,
        # create it. Then continue on, one descendant at a time, either adding
        # new levels or using the existing ones if they're already there 
        # from previous group pages. 
        for grouppage in GroupPage.objects.live().filter(is_active=True):
            ancestors = [GroupIndexPage.objects.first()] + list(GroupPage.objects.ancestor_of(grouppage)) + [grouppage]
            currentlevel = groups_active
            while ancestors:
                ancestor = ancestors.pop(0)
                if str(ancestor.content_type) in ['group page', 'group index page']:
                    nextlevels = list(filter(lambda g: g['url'] == ancestor.url, currentlevel))
                    if nextlevels:
                        currentlevel = nextlevels[0]['children']
                    else:
                        newnode = {
                            'title': ancestor.title,
                            'url': ancestor.url,
                            'children': [],
                        }
                        currentlevel.append(newnode)
                        currentlevel = newnode['children']

        def alphabetize_groups(currentlevel):
            for node in currentlevel:
                node['children'] = alphabetize_groups(node['children'])
            return sorted(currentlevel, key=lambda c: c['title'])
        groups_active = alphabetize_groups(groups_active)

        def get_html(currentlevel):
            if not currentlevel:
                return ''
            else:
                return "<ul>" + "".join(list(map(lambda n: "<li><a href='" + n['url'] + "'>" + n['title'] + "</a>" + get_html(n['children']) + "</li>", currentlevel))) + "</ul>"
        groups_active_html = get_html(groups_active[0]['children'])
        
        context['groups_active_html'] = groups_active_html
        context['groups_inactive'] = list(map(lambda g: { 'title': g.title, 'url': g.url }, GroupPage.objects.live().filter(is_active=False).order_by('title')))
        return context
