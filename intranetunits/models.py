from base.models import BasePage, DefaultBodyFields, Email, PhoneNumber, Report
from django.db import models
from django.db.models.fields import CharField, TextField
from modelcluster.fields import ParentalKey
from staff.models import StaffPage, StaffPagePageVCards, VCard
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel, StreamFieldPanel
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailcore.models import Orderable, Page

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

    intro = StreamField(DefaultBodyFields(), blank=True)

    internal_location = models.CharField(max_length=255, blank=True)

    internal_phone_number = models.CharField(max_length=255, blank=True)

    internal_email = models.EmailField(max_length=255, blank=True)

    staff_only_email = models.EmailField(max_length=254, blank=True)
    
    body = StreamField(DefaultBodyFields(), null=True, blank=True)

    subpage_types = ['intranetunits.IntranetUnitsPage', 'base.IntranetPlainPage']

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

        department_members = []
        if self.specific.unit:
            units = self.specific.unit.get_descendants(True)
    
            staff_pages = []
            for v in StaffPagePageVCards.objects.filter(unit__in=units):
                staff_page = v.staffpagepagevcards.page
                if staff_page not in staff_pages:
                    staff_pages.append(staff_page)

            for staff_page in staff_pages:
                titles = []
                emails = []
                phone_numbers = []
                for v in StaffPagePageVCards.objects.filter(page=staff_page, unit__in=units):
                    if not v.title in titles:
                        titles.append(v.title)
                    if not v.email in emails:
                        emails.append(v.email)
                    if not v.phone_number in phone_numbers:
                        phone_numbers.append(v.phone_number)

                if len(emails) > 0:
                    email = emails[0]
                else:
                    email = ''

                department_members.append({
                    'title': staff_page.title,
                    'url': staff_page.url,
                    'jobtitle': "<br/>".join(titles),
                    'email': email,
                    'phone': "<br/>".join(phone_numbers),
                })

        department_members = sorted(department_members, key=lambda s: s['title'])
        context['department_members'] = department_members
        return context

IntranetUnitsPage.content_panels = Page.content_panels + [
    StreamFieldPanel('intro'),
    FieldPanel('unit'),
    MultiFieldPanel(
        [
            FieldPanel('internal_location'),
            FieldPanel('internal_phone_number'),
            FieldPanel('internal_email'),
        ],
        heading="Staff-only Contact Information",
    ),
    InlinePanel('intranet_unit_reports', label='Staff-Only Reports'),
    StreamFieldPanel('body')
] + BasePage.content_panels


class IntranetUnitPageReports(Orderable, Report):
    """
    Reports for intranet unit pages.
    """
    page = ParentalKey('intranetunits.IntranetUnitsPage', related_name='intranet_unit_reports')

class IntranetUnitsIndexPage(BasePage):
    intro = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ] + BasePage.content_panels

    subpage_types = ['base.IntranetPlainPage', 'intranetunits.IntranetUnitsPage']
