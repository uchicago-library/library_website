from base.models import BasePage, DefaultBodyFields, Email, PhoneNumber, Report
from group.models import get_page_objects_grouped_by_date, get_page_objects_as_list, enforce_name_as_year, enforce_name_as_reports
from directory_unit.models import DirectoryUnit, UnitSupervisor
from django.db import models
from django.db.models.fields import CharField, TextField
from modelcluster.fields import ParentalKey
from staff.models import StaffPage, StaffPagePageVCards, VCard
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel, StreamFieldPanel
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailcore.models import Orderable, Page
from wagtail.wagtailsearch import index
from django.core.exceptions import ValidationError

class IntranetUnitsReportsPageTable(Orderable, Report):
    """
    Reports for intranet unit pages.
    """
    page = ParentalKey('intranetunits.IntranetUnitsReportsPage', related_name='intranet_units_reports')


class IntranetUnitsReportsIndexPage(BasePage):
    """
    Index page for holding reports.
    """
    content_panels = Page.content_panels + BasePage.content_panels
    subpage_types = ['intranetunits.IntranetUnitsReportsPage']

    def clean(self):
        """
        Make sure page titles adhere to strict
        formatting policy.
        """
        enforce_name_as_reports(self.title)

    def get_context(self, request):
        """
        Get reports from children.
        """
        context = super(IntranetUnitsReportsIndexPage, self).get_context(request)
        year_pages = Page.objects.live().descendant_of(self.get_parent()).type(IntranetUnitsReportsPage).order_by('-title')

        data = []
        for page in year_pages:
            year_title = page.title
            year_reports = page.intranetunitsreportspage.get_reports_grouped_by_date()
            data.append((year_title, year_reports))

        context['data'] = data
        return context


class IntranetUnitsReportsPage(BasePage):
    content_panels = Page.content_panels + [
        InlinePanel('intranet_units_reports', label='Reports'),
    ] + BasePage.content_panels 

    subpage_types = ['base.IntranetPlainPage']

    def clean(self):
        """
        Make sure page titles adhere to strict
        formatting policy.
        """
        enforce_name_as_year(self.title)

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


class IntranetUnitsPage(BasePage, Email, PhoneNumber):
    """
    Content type for department pages on the intranet. 
    """

    unit = models.ForeignKey(
        'directory_unit.DirectoryUnit',
        related_name='intranet_unit_page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

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

    subpage_types = ['base.IntranetIndexPage', 'base.IntranetPlainPage', 'intranetforms.IntranetFormPage', \
    'intranettocs.TOCPage', 'intranetunits.IntranetUnitsPage', 'intranetunits.IntranetUnitsReportsIndexPage']

    search_fields = BasePage.search_fields + [
        index.SearchField('intro'),
        index.SearchField('internal_location'),
        index.SearchField('internal_phone_number'),
        index.SearchField('internal_email'),
        index.SearchField('staff_only_email'),
        index.SearchField('body'),
    ]

    def get_context(self, request):
        context = super(IntranetUnitsPage, self).get_context(request)

        context['phone'] = ''
        if self.specific.internal_phone_number:
            context['phone'] = self.specific.internal_phone_number

        context['location'] = ''
        if self.specific.internal_location: 
            context['location'] = self.specific.internal_location

        context['email'] = ''
        if  self.specific.internal_email:
            context['email'] = self.specific.internal_email

        context['show_staff'] = self.show_staff

        context['show_departments'] = self.show_departments

        department_members = []
        if self.specific.unit:
            units = self.specific.unit.get_descendants(True)
    
            staff_pages = []
            for v in StaffPagePageVCards.objects.filter(page__live=True, unit__in=units):
                staff_page = v.staffpagepagevcards.page
                if staff_page not in staff_pages:
                    staff_pages.append(staff_page)

            # sorting: supervisors first, alphabetically; then non-supervisors, alphabetically. 
            supervisors = list(map(lambda u: u.supervisor, UnitSupervisor.objects.filter(unit=self.specific.unit)))
            supervisor_staff = sorted(list(set(staff_pages).intersection(supervisors)), key=lambda s: s.title)
            non_supervisor_staff = sorted(list(set(staff_pages).difference(supervisors)), key=lambda s: s.title)
            staff_pages = supervisor_staff + non_supervisor_staff 

            for staff_page in staff_pages:
                email = staff_page.staff_page_email.first().email
                phone_numbers = staff_page.staff_page_phone_faculty_exchange.all().values_list('phone_number', flat=True) 
                titles = [staff_page.position_title]

                department_members.append({
                    'title': staff_page.title,
                    'url': staff_page.url,
                    'jobtitle': "<br/>".join(titles),
                    'email': email,
                    'phone': "<br/>".join(phone_numbers),
                })

        context['department_members'] = department_members

        department_units = []
        if self.unit:
            for directory_unit in DirectoryUnit.objects.filter(parentUnit=self.unit):
                intranet_unit_pages = directory_unit.intranet_unit_page.all().filter(live=True, show_in_menus=True)
                if intranet_unit_pages:
                    unit = {
                        'title': intranet_unit_pages[0].title,
                        'url': intranet_unit_pages[0].url,
                        'location': intranet_unit_pages[0].internal_location,
                        'phone_number': intranet_unit_pages[0].internal_phone_number,
                        'email': intranet_unit_pages[0].internal_email
                    }
                   
                    supervisors = [] 
                    for s in UnitSupervisor.objects.filter(unit=directory_unit):
                        if s.supervisor != None:
                            try:
                                email = s.supervisor.staff_page_email.first().email
                            except AttributeError:
                                email = ''
                            try:
                                phone_number = s.supervisor.staff_page_phone_faculty_exchange.first().phone_number
                            except AttributeError:
                                phone_number = ''

                            supervisors.append({
                                'title': s.supervisor.title,
                                'url': s.supervisor.url,
                                'phone_number': phone_number,
                                'email': email
                            })
                    unit['supervisors'] = supervisors
                    department_units.append(unit)

        # split the department units into lists of lists, each inner list containing 4 or less items.
        context['department_unit_rows'] = [department_units[i:i+4] for i in range(0, len(department_units), 4)]

        #reports
        tmp = []
        unit_reports_pages = IntranetUnitsReportsPage.objects.descendant_of(self)
        for unit_reports_page in unit_reports_pages:
            for r in unit_reports_page.intranet_units_reports.all():
                if not r.link and not r.document.url:
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
    FieldPanel('unit'),
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
    intro = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ] + BasePage.content_panels

    subpage_types = ['base.IntranetIndexPage', 'base.IntranetPlainPage', 'intranetunits.IntranetUnitsPage']

    search_fields = BasePage.search_fields + [
        index.SearchField('intro'),
    ]

    def get_context(self, request):
        context = super(IntranetUnitsIndexPage, self).get_context(request)

        units = [{
            'title': IntranetUnitsIndexPage.objects.first().title,
            'url': IntranetUnitsIndexPage.objects.first().url,
            'children': [],
        }]

        # for each unit page get a list of the page's "intranet units page" or
        # "intranet units index page" ancestors. Check to see if this
        # particular ancestor already exists in the units tree. If it doesn't
        # exist, create it. Then continue on, one descendant at a time, either
        # adding new levels or using the existing ones if they're already there
        # from previous unit pages. 
        for intranetunitspage in IntranetUnitsPage.objects.live():
            ancestors = [IntranetUnitsIndexPage.objects.first()] + list(IntranetUnitsPage.objects.ancestor_of(intranetunitspage)) + [intranetunitspage]
            currentlevel = units
            while ancestors:
                ancestor = ancestors.pop(0)
                if str(ancestor.content_type) in ['intranet units page', 'intranet units index page']:
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

        def alphabetize_units(currentlevel):
            for node in currentlevel:
                node['children'] = alphabetize_units(node['children'])
            return sorted(currentlevel, key=lambda c: c['title'])
        units = alphabetize_units(units)

        def get_html(currentlevel):
            if not currentlevel:
                return ''
            else:
                return "<ul>" + "".join(list(map(lambda n: "<li><a href='" + n['url'] + "'>" + n['title'] + "</a>" + get_html(n['children']) + "</li>", currentlevel))) + "</ul>"
        units_html = get_html(units[0]['children'])
        context['units_html'] = units_html
        return context

