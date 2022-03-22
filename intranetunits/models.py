from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (
    FieldPanel, InlinePanel, MultiFieldPanel, StreamFieldPanel
)
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Orderable, Page
from wagtail.search import index

from base.models import BasePage, DefaultBodyFields, Email, PhoneNumber, Report
from base.utils import get_doc_titles_for_indexing, get_field_for_indexing
from group.models import (
    get_page_objects_as_list, get_page_objects_grouped_by_date
)
from staff.models import StaffPage

INTRANET_UNIT_PAGE_CONTENT_TYPES = [
    'intranetunits | intranet units page',
    'intranetunits | intranet units index page'
]


class IntranetUnitsReportsPageTable(Orderable, Report):
    """
    Reports for intranet unit pages.
    """
    page = ParentalKey(
        'intranetunits.IntranetUnitsReportsPage',
        related_name='intranet_units_reports'
    )


class IntranetUnitsReportsIndexPage(BasePage):
    """
    Index page for holding reports.
    """
    content_panels = Page.content_panels + BasePage.content_panels
    subpage_types = ['intranetunits.IntranetUnitsReportsPage']

    def get_context(self, request):
        """
        Get reports from children.
        """
        context = super(IntranetUnitsReportsIndexPage,
                        self).get_context(request)
        year_pages = self.get_children().order_by('-title')

        data = []
        for page in year_pages:
            year_title = page.title
            year_reports = page.intranetunitsreportspage.get_reports_grouped_by_date(
            )
            data.append((year_title, year_reports))

        context['data'] = data
        return context


class IntranetUnitsReportsPage(BasePage):
    content_panels = Page.content_panels + [
        InlinePanel('intranet_units_reports', label='Reports'),
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
        context = super(IntranetUnitsReportsPage, self).get_context(request)
        reports = self.get_reports_grouped_by_date()
        context['reports'] = reports
        return context

    def get_reports(self):
        """
        Get group reports as a list.

        Returns:
            list
        """
        return get_page_objects_as_list(self.intranet_units_reports)

    def get_reports_grouped_by_date(self):
        """
        Get reports grouped by date.

        Returns:
            OrderedDict
        """
        return get_page_objects_grouped_by_date(self.intranet_units_reports)

    def get_report_summaries_for_indexing(self):
        """
        Get report summaries in order to index them.

        Returns:
            Concatonated string of all meeting minute sumaries for
            indexing purposes.
        """
        return get_field_for_indexing(
            'summary', self.intranet_units_reports.values()
        )

    def get_report_doc_links_for_indexing(self):
        """
        Get meeting minute document links in order to index them.

        Returns:
            Concatonated string of all meeting minute document titles for
            document links. Used for indexing purposes.
        """
        return get_doc_titles_for_indexing(
            'link_document_id', self.intranet_units_reports.values()
        )


class IntranetUnitsPage(BasePage, Email, PhoneNumber):
    """
    Content type for department pages on the intranet.
    """

    unit_page = models.ForeignKey(
        'units.UnitPage',
        related_name='loop_page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    intro = StreamField(DefaultBodyFields(), blank=True)
    internal_location = models.CharField(max_length=255, blank=True)
    internal_phone_number = models.CharField(max_length=255, blank=True)
    internal_email = models.EmailField(max_length=255, blank=True)
    staff_only_email = models.EmailField(max_length=254, blank=True)
    body = StreamField(DefaultBodyFields(), null=True, blank=True)
    show_staff = models.BooleanField(default=False)
    show_departments = models.BooleanField(default=False)

    subpage_types = [
        'base.IntranetIndexPage', 'base.IntranetPlainPage',
        'intranetforms.IntranetFormPage', 'intranettocs.TOCPage',
        'intranetunits.IntranetUnitsPage',
        'intranetunits.IntranetUnitsReportsIndexPage'
    ]

    search_fields = BasePage.search_fields + [
        index.SearchField('intro'),
        index.SearchField('internal_location'),
        index.SearchField('internal_phone_number'),
        index.SearchField('internal_email'),
        index.SearchField('staff_only_email'),
        index.SearchField('body'),
    ]

    def _get_full_name_list(self):
        """
        Helper function for get_full_name() and
        get_campus_directory_full_name(). This returns a list of page titles
        that can be processed by those two functions.
        """
        return list(
            self.get_ancestors(True).live().type(IntranetUnitsPage).values_list(
                'title', flat=True
            )
        )

    def get_full_name(self):
        """
        Get an IntranetUnitsPage's full name according to Wagtail.

        The full name of an IntranetUnitsPage includes a breadcrumb trail of
        the titles its ancestor IntranetUnitsPages.

        Example:
        Wagtail contains an IntranetUnitsPage for "Collections & Access". That
        page contains "Access Services". The full name for Access Services is
        "Collections & Access - Access Services".

        Compare this method's output with get_campus_directory_full_name().
        """
        return ' - '.join(self._get_full_name_list())

    def get_campus_directory_full_name(self):
        """
        Get an IntranetUnitsPage's campus directory name.

        The campus directory describes a university department in a three level
        heirarchy: division, department, and sub-department. For library
        departments division is always "Library".

        The library's own view of its org chart has more levels than what we
        can represent in the campus directory, so we skip some levels to make
        room for the departments below it. Those levels are hardcoded below.

        Example:
        Wagail contains an IntranetUnitsPage for "Collections & Access - Access
        Services". The campus directory full name for Access Services should be
        "Access Services".
        """
        titles = self._get_full_name_list()

        # Remove "container units". These are top-level units in the library's
        # system that aren't present in the campus directory.
        skip_containing_units = ['Collections & Access', 'Research & Learning']
        for v in skip_containing_units:
            try:
                titles.remove(v)
            except ValueError:
                continue

        # Our system includes more than two levels of heiarchy, but the campus
        # directory only includes two.
        titles = titles[:2]

        return ' - '.join(titles)

    def get_context(self, request):
        context = super(IntranetUnitsPage, self).get_context(request)

        context['phone'] = ''
        if self.specific.internal_phone_number:
            context['phone'] = self.specific.internal_phone_number

        context['location'] = ''
        if self.specific.internal_location:
            context['location'] = self.specific.internal_location

        context['email'] = ''
        if self.specific.internal_email:
            context['email'] = self.specific.internal_email

        context['show_staff'] = self.show_staff

        context['show_departments'] = self.show_departments

        department_members = []
        if self.specific.unit_page:
            unit_pages = self.specific.unit_page.get_descendants(True)
            staff_pages = StaffPage.objects.live().filter(
                staff_page_units__library_unit__in=unit_pages
            ).distinct()

            # sorting: supervisors first, alphabetically; then non-supervisors, alphabetically.
            supervisor = self.specific.unit_page.department_head
            if supervisor:
                staff_pages = [supervisor] + list(
                    staff_pages.exclude(pk=supervisor.pk).order_by('last_name')
                )
            else:
                staff_pages = list(staff_pages.order_by('last_name'))

            for staff_page in staff_pages:
                try:
                    email = staff_page.staff_page_email.first().email
                except AttributeError:
                    email = None
                phone_numbers = staff_page.staff_page_phone_faculty_exchange.all(
                ).values_list('phone_number', flat=True)
                titles = []
                if staff_page.position_title:
                    titles = [staff_page.position_title]

                department_members.append(
                    {
                        'title': staff_page.title,
                        'url': staff_page.url,
                        'jobtitle': "<br/>".join(titles),
                        'email': email,
                        'phone': "<br/>".join(phone_numbers),
                    }
                )

        context['department_members'] = department_members

        department_units = []
        try:
            for unit_page in self.unit_page.get_descendants():
                intranet_unit_page = unit_page.specific.loop_page.live().filter(
                    show_in_menus=True
                ).first()
                if intranet_unit_page:
                    unit = {
                        'title': intranet_unit_page.title,
                        'url': intranet_unit_page.url,
                        'location': intranet_unit_page.internal_location,
                        'phone_number':
                        intranet_unit_page.internal_phone_number,
                        'email': intranet_unit_page.internal_email
                    }

                    supervisors = []
                    if unit_page.specific.department_head:
                        try:
                            email = unit_page.specific.department_head.staff_page_email.first(
                            ).email
                        except AttributeError:
                            email = ''
                        try:
                            phone_number = unit_page.specific.department_head.staff_page_phone_faculty_exchange.first(
                            ).phone_number
                        except AttributeError:
                            phone_number = ''

                        supervisors.append(
                            {
                                'title':
                                unit_page.specific.department_head.title,
                                'url': unit_page.specific.department_head.url,
                                'phone_number': phone_number,
                                'email': email
                            }
                        )
                    unit['supervisors'] = supervisors
                    department_units.append(unit)
        except (AttributeError):
            pass

        # split the department units into lists of lists, each inner list containing 4 or less items.
        context['department_unit_rows'] = [
            department_units[i:i + 4]
            for i in range(0, len(department_units), 4)
        ]

        # reports
        tmp = []
        unit_reports_pages = IntranetUnitsReportsPage.objects.descendant_of(
            self
        )
        for unit_reports_page in unit_reports_pages:
            for r in unit_reports_page.intranet_units_reports.all():
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

        context['reports'] = reports

        return context


IntranetUnitsPage.content_panels = Page.content_panels + [
    StreamFieldPanel('intro'),
    FieldPanel('unit_page'),
    MultiFieldPanel(
        [
            FieldPanel('internal_location'),
            FieldPanel('internal_phone_number'),
            FieldPanel('internal_email'),
        ],
        heading="Staff-only Contact Information",
    ),
    StreamFieldPanel('body')
] + BasePage.content_panels + [
    MultiFieldPanel(
        [
            FieldPanel('show_staff'),
            FieldPanel('show_departments'),
        ],
        heading="Show staff or subdepartments on this page"
    )
]


class IntranetUnitsIndexPage(BasePage):
    max_count = 1
    intro = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ] + BasePage.content_panels

    subpage_types = ['intranetunits.IntranetUnitsPage']

    search_fields = BasePage.search_fields + [
        index.SearchField('intro'),
    ]

    def get_context(self, request):
        context = super(IntranetUnitsIndexPage, self).get_context(request)

        units = [
            {
                'title': IntranetUnitsIndexPage.objects.first().title,
                'url': IntranetUnitsIndexPage.objects.first().url,
                'children': [],
            }
        ]

        # for each unit page get a list of the page's "intranet units page" or
        # "intranet units index page" ancestors. Check to see if this
        # particular ancestor already exists in the units tree. If it doesn't
        # exist, create it. Then continue on, one descendant at a time, either
        # adding new levels or using the existing ones if they're already there
        # from previous unit pages.
        for intranetunitspage in IntranetUnitsPage.objects.live():
            ancestors = [IntranetUnitsIndexPage.objects.first()] + list(
                IntranetUnitsPage.objects.ancestor_of(intranetunitspage)
            ) + [intranetunitspage]
            currentlevel = units
            while ancestors:
                ancestor = ancestors.pop(0)
                if str(
                    ancestor.content_type
                ) in INTRANET_UNIT_PAGE_CONTENT_TYPES:
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

        def alphabetize_units(currentlevel):
            for node in currentlevel:
                node['children'] = alphabetize_units(node['children'])
            return sorted(currentlevel, key=lambda c: c['title'])

        units = alphabetize_units(units)

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

        units_html = get_html(units[0]['children'])
        context['units_html'] = units_html
        return context
