import re
from collections import OrderedDict
from datetime import datetime, timedelta

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.fields import CharField
from django.utils import timezone
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (
    FieldPanel, InlinePanel, MultiFieldPanel, PageChooserPanel, StreamFieldPanel
)
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Orderable, Page
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from base.models import (
    AbstractReport, BasePage, DefaultBodyFields, Email, Report
)
from base.utils import get_doc_titles_for_indexing, get_field_for_indexing

GROUP_PAGE_CONTENT_TYPES = ['group | group page', 'group | group index page']


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


def enforce_name_as_year(title):
    """
    Helper function for making sure
    page titles adhere to a strict
    formatting policy.
    """
    if not re.match('^[0-9]{4}$', title):
        raise ValidationError(
            {
                'title': (
                    'Please enter the year as \
            a four digit number, e.g. 2016'
                )
            }
        )


def get_page_objects_grouped_by_date(obj):
    """
    Helper function for getting page objects and
    child objects grouped by date.
    Used for meeting minutes and reports.

    Args:
        obj: Page.child_object that belongs to a Page type.
        Must have "date" and "summary" fields associated
        with it. Other optional fields on the object
        can be "link" and "document" (wagtail doc obj).

    Returns:
        OrderedDict
    """
    retval = OrderedDict()
    for i in obj.order_by('-date'):
        if not i.link and not i.document.url:
            continue

        date = i.date.strftime("%b. %-d, %Y")
        item = {'summary': i.summary}

        if i.link:
            item['url'] = i.link
        elif m.document.url:
            item['url'] = i.document.url

        if date in retval:
            retval[date].append(item)
        else:
            retval[date] = [item]
    return retval


def get_page_objects_as_list(obj):
    """
    Helper function for getting page objects and
    child objects as a list.
    Used for meeting minutes and reports.

    Args:
        obj: Page.child_object that belongs to a Page type.
        Must have "date" and "summary" fields associated
        with it. Other optional fields on the object
        can be "link" and "document" (wagtail doc obj).

    Returns: list
    """
    retval = []
    for i in obj.order_by('-date'):
        if not i.link and not i.document.url:
            continue
        item = {'summary': i.summary, 'date': i.date.strftime("%b. %-d, %Y")}
        if i.link:
            item['url'] = i.link
        elif m.document.url:
            item['url'] = m.document.url
        retval.append(item)

    return retval


class MeetingMinutes(AbstractReport):
    """
    Meeting minutes content type.
    """
    link_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    panels = [
        FieldPanel('date'),
        FieldPanel('summary'),
        PageChooserPanel('link_page'),
    ]

    class Meta:
        abstract = True


class GroupMeetingMinutesPageTable(Orderable, MeetingMinutes):
    """
    Meeting minutes for group pages.
    """
    page = ParentalKey(
        'group.GroupMeetingMinutesPage', related_name='meeting_minutes'
    )


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
        on_delete=models.CASCADE
    )

    group_member = models.ForeignKey(
        'staff.StaffPage',
        related_name='member',
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    role = models.ForeignKey(
        'group.GroupMemberRole',
        on_delete=models.SET_NULL,
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
    subpage_types = [
        'base.IntranetIndexPage', 'base.IntranetPlainPage', 'group.GroupPage',
        'group.GroupMeetingMinutesIndexPage', 'group.GroupReportsIndexPage',
        'intranetforms.IntranetFormPage', 'projects.ProjectPage', 'redirects.LoopRedirectPage'
    ]
    meeting_location = CharField(blank=True, max_length=255)
    meeting_start_time = models.TimeField(
        auto_now=False,
        auto_now_add=False,
        default=timezone.now,
        blank=True,
        null=True
    )
    meeting_end_time = models.TimeField(
        auto_now=False,
        auto_now_add=False,
        default=default_end_time,
        blank=True,
        null=True
    )
    meeting_frequency = CharField(blank=True, max_length=255)
    intro = StreamField(DefaultBodyFields(), blank=True)
    is_active = models.BooleanField(default=True)
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

    search_fields = BasePage.search_fields + [
        index.SearchField('meeting_location'),
        index.SearchField('meeting_frequency'),
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    def get_context(self, request):

        context = super(GroupPage, self).get_context(request)
        group_members = self.group_members.all()

        # sorting: chairs or co-chairs first, alphabetically; then others, alphabetically.
        group_member_chairs = []
        non_group_member_chairs = []
        for g in group_members:
            if g.group_member == None:
                continue
            if g.group_member.live == False:
                continue
            if g.role and g.role.text in ['Chair', 'Co-Chair']:
                group_member_chairs.append(g)
            else:
                non_group_member_chairs.append(g)

        group_member_chairs = sorted(
            group_member_chairs, key=lambda g: g.group_member.title
        )
        non_group_member_chairs = sorted(
            non_group_member_chairs, key=lambda g: g.group_member.title
        )
        group_members = group_member_chairs + non_group_member_chairs

        # minutes
        tmp = []
        group_meeting_min_pages = GroupMeetingMinutesPage.objects.descendant_of(
            self
        )
        for group_meeting_min_page in group_meeting_min_pages:
            for m in group_meeting_min_page.meeting_minutes.all():
                try:
                    if not m.link and not m.document.url:
                        continue
                except AttributeError:
                    continue
                minute = {
                    'summary': m.summary,
                    'date': m.date.strftime("%b. %-d, %Y"),
                    'sortdate': m.date.strftime("%Y%m%d")
                }
                if m.link:
                    minute['url'] = m.link
                elif m.document.url:
                    minute['url'] = m.document.url
                tmp.append(minute)
        minutes = sorted(tmp, key=lambda m: m['sortdate'], reverse=True)[:3]

        # reports
        tmp = []
        group_reports_pages = GroupReportsPage.objects.descendant_of(self)
        for group_reports_page in group_reports_pages:
            for r in group_reports_page.group_reports.all():
                try:
                    if not r.link and not r.document.url:
                        continue
                except AttributeError:
                    continue
                report = {
                    'summary': r.summary,
                    'date': r.date.strftime("%b. %-d, %Y"),
                    'sortdate': r.date.strftime("%Y%m%d")
                }
                if r.link:
                    report['url'] = r.link
                elif r.document.url:
                    report['url'] = r.document.url
                tmp.append(report)
        reports = sorted(tmp, key=lambda r: r['sortdate'], reverse=True)[:3]

        context['minutes'] = minutes
        context['reports'] = reports
        context['group_members'] = list(
            map(
                lambda m: {
                    'title':
                    m.group_member.title,
                    'unit':
                    '<br/>'.join(
                        sorted(
                            map(
                                lambda u: u.library_unit.get_full_name(),
                                m.group_member.staff_page_units.all()
                            )
                        )
                    ),
                    'url':
                    m.group_member.url,
                    'role':
                    m.role
                }, group_members
            )
        )
        return context


class GroupMeetingMinutesIndexPage(BasePage):
    """
    Index page for holding meeting minute pages.
    """
    content_panels = Page.content_panels + BasePage.content_panels
    subpage_types = ['group.GroupMeetingMinutesPage']

    def clean(self):
        """
        Make sure page titles adhere to strict
        formatting policy.
        """
        if not self.title.strip() == "Meeting Minutes":
            raise ValidationError(
                {'title': ('The title should be "Meeting Minutes"')}
            )

    def get_context(self, request):
        """
        Get meeting minutes from children.
        """
        context = super(GroupMeetingMinutesIndexPage, self).get_context(request)

        year_pages = self.get_children().order_by('-title')

        data = []
        for page in year_pages:
            year_title = page.title
            year_minutes = page.groupmeetingminutespage.get_meeting_minutes_grouped_by_date(
            )
            data.append((year_title, year_minutes))

        context['data'] = data
        return context


class GroupMeetingMinutesPage(BasePage):
    """
    Page class that acts as a receptacle for meeting minutes.
    Objects created with this class should represent a year
    and they should hold all of the meeting minutes for the
    given year.
    """
    content_panels = Page.content_panels + [
        InlinePanel('meeting_minutes', label='Meeting Minutes'),
    ] + BasePage.content_panels

    search_fields = BasePage.search_fields + [
        index.SearchField('get_mm_summaries_for_indexing', partial_match=True),
        index.SearchField('get_mm_doc_links_for_indexing', partial_match=True),
    ]

    subpage_types = ['base.IntranetPlainPage']

    def clean(self):
        """
        Make sure page titles adhere to strict
        formatting policy.
        """
        enforce_name_as_year(self.title)

    def get_meeting_minutes(self):
        """
        Get meeting minutes as a list.

        Returns: list
        """
        return get_page_objects_as_list(self.meeting_minutes)

    def get_meeting_minutes_grouped_by_date(self):
        """
        Get meeting minutes grouped by date.

        Returns:
            OrderedDict
        """
        return get_page_objects_grouped_by_date(self.meeting_minutes)

    def get_context(self, request):
        """
        Override get_context.
        """
        context = super(GroupMeetingMinutesPage, self).get_context(request)
        minutes = self.get_meeting_minutes()
        context['minutes'] = minutes
        return context

    def get_mm_summaries_for_indexing(self):
        """
        Get meeting minute summaries in order to index them.

        Returns:
            Concatonated string of all meeting minute sumaries for
            indexing purposes.
        """
        return get_field_for_indexing('summary', self.meeting_minutes.values())

    def get_mm_doc_links_for_indexing(self):
        """
        Get meeting minute document links in order to index them.

        Returns:
            Concatonated string of all meeting minute document titles for
            document links. Used for indexing purposes.
        """
        return get_doc_titles_for_indexing(
            'link_document_id', self.meeting_minutes.values()
        )


class GroupReportsIndexPage(BasePage):
    """
    Index page for holding reports.
    """
    content_panels = Page.content_panels + BasePage.content_panels
    subpage_types = ['group.GroupReportsPage']

    def get_context(self, request):
        """
        Get reports from children.
        """
        context = super(GroupReportsIndexPage, self).get_context(request)

        year_pages = self.get_children().order_by('-title')

        data = []
        for page in year_pages:
            year_title = page.title
            year_reports = page.groupreportspage.get_reports_grouped_by_date()
            data.append((year_title, year_reports))

        context['data'] = data
        return context


class GroupReportsPage(BasePage):
    """
    Page class that acts as a receptacle for reports.
    Objects created with this class should represent a year
    and they should hold all of the reports for the
    given year.
    """
    content_panels = Page.content_panels + [
        InlinePanel('group_reports', label='Reports'),
    ] + BasePage.content_panels

    search_fields = BasePage.search_fields + [
        index.
        SearchField('get_report_summaries_for_indexing', partial_match=True),
        index.
        SearchField('get_report_doc_links_for_indexing', partial_match=True),
    ]

    subpage_types = ['base.IntranetPlainPage']

    def get_context(self, request):
        """
        Override get_context
        """
        context = super(GroupReportsPage, self).get_context(request)
        reports = self.get_reports_grouped_by_date()
        context['reports'] = reports
        return context

    def get_reports(self):
        """
        Get group reports as a list.

        Returns:
            list
        """
        return get_page_objects_as_list(self.group_reports)

    def get_reports_grouped_by_date(self):
        """
        Get reports grouped by date.

        Returns:
            OrderedDict
        """
        return get_page_objects_grouped_by_date(self.group_reports)

    def get_report_summaries_for_indexing(self):
        """
        Get report summaries in order to index them.

        Returns:
            Concatonated string of all meeting minute sumaries for
            indexing purposes.
        """
        return get_field_for_indexing('summary', self.group_reports.values())

    def get_report_doc_links_for_indexing(self):
        """
        Get meeting minute document links in order to index them.

        Returns:
            Concatonated string of all meeting minute document titles for
            document links. Used for indexing purposes.
        """
        return get_doc_titles_for_indexing(
            'link_document_id', self.group_reports.values()
        )


class GroupIndexPage(BasePage):
    """
    Receptacle page for holding groups.
    """
    max_count = 1
    subpage_types = ['group.GroupPage']
    intro = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ] + BasePage.content_panels

    search_fields = BasePage.search_fields + [
        index.SearchField('intro'),
    ]

    def get_context(self, request):
        context = super(GroupIndexPage, self).get_context(request)

        groups_active = [
            {
                'title': GroupIndexPage.objects.first().title,
                'url': GroupIndexPage.objects.first().url,
                'children': [],
            }
        ]

        # for each group page get a list of the page's "group page" or "group
        # index page" ancestors. Check to see if this particular ancestor
        # already exists in the groups_active tree. If it doesn't exist,
        # create it. Then continue on, one descendant at a time, either adding
        # new levels or using the existing ones if they're already there
        # from previous group pages.
        for grouppage in GroupPage.objects.live().filter(is_active=True):
            ancestors = [GroupIndexPage.objects.first()] + list(
                GroupPage.objects.ancestor_of(grouppage)
            ) + [grouppage]
            currentlevel = groups_active
            while ancestors:
                ancestor = ancestors.pop(0)
                if str(ancestor.content_type) in GROUP_PAGE_CONTENT_TYPES:
                    nextlevels = list(
                        filter(
                            lambda g: g['url'] == ancestor.url, currentlevel
                        )
                    )
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
                return "<ul>" + "".join(
                    list(
                        map(
                            lambda n: "<li><a href='" + n['url'] + "'>" + n[
                                'title'] + "</a>" + get_html(n['children']) +
                            "</li>", currentlevel
                        )
                    )
                ) + "</ul>"

        groups_active_html = get_html(groups_active[0]['children'])

        context['groups_active_html'] = groups_active_html
        context['groups_inactive'] = list(
            map(
                lambda g: {
                    'title': g.title,
                    'url': g.url
                },
                GroupPage.objects.live().filter(is_active=False
                                                ).order_by('title')
            )
        )
        return context
