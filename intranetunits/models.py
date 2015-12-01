from base.models import BasePage, DefaultBodyFields, Email, PhoneNumber, Report
from django.db import models
from django.db.models.fields import CharField, TextField
from modelcluster.fields import ParentalKey
from staff.models import StaffPage
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel, StreamFieldPanel
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailcore.models import Orderable, Page

class IntranetUnitsPage(BasePage, Email, PhoneNumber):
    """
    Content type for department pages on the intranet. 
    """

    unit = models.ForeignKey(
        'units.UnitPage',
        related_name='intranet_unit_page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    intro = StreamField(DefaultBodyFields(), blank=True)
    # internal location
    # staff-only phone number
    staff_only_email = models.EmailField(max_length=254, blank=True)
    # reports. 
    
    body = StreamField(DefaultBodyFields(), null=True, blank=True)

    subpage_types = ['intranetunits.IntranetUnitsPage', 'base.IntranetPlainPage']

IntranetUnitsPage.content_panels = Page.content_panels + [
    StreamFieldPanel('intro'),
    InlinePanel('intranet_unit_reports', label='Staff-Only Reports'),
    StreamFieldPanel('body')
] + BasePage.content_panels

class IntranetUnitPageReports(Orderable, Report):
    """
    Reports for intranet unit pages.
    """
    page = ParentalKey('intranetunits.IntranetUnitsPage', related_name='intranet_unit_reports')

class IntranetUnitsIndexPage(Page):
    intro = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ]

    subpage_types = ['intranetunits.IntranetUnitsPage']
