from django.db import models
from library_website.settings.base import PHONE_FORMAT, PHONE_ERROR_MSG
from wagtail.wagtailcore.models import Orderable, Page
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel, PageChooserPanel, StreamFieldPanel
from wagtail.wagtailsearch import index
from wagtail.wagtailsnippets.models import register_snippet
from wagtail.wagtailsnippets.edit_handlers import SnippetChooserPanel
from modelcluster.fields import ParentalKey
from django.core.validators import RegexValidator
from base.models import BasePage, DefaultBodyFields, PhoneNumber, FaxNumber, Report

@register_snippet
class Role(models.Model, index.Indexed):
    """
    Snippet for roles.
    """
    text = models.CharField(max_length=255, blank=False)

    panels = [
        FieldPanel('text'),
    ]

    class Meta:
        verbose_name = 'Unit Role'
        verbose_name_plural = 'Unit Roles'

    def __str__(self):
        return self.text

    search_fields = [
        index.SearchField('text', partial_match=True),
    ]


class UnitPageRolePlacement(Orderable, models.Model):
    """
    Through table for linking Role snippets to UnitPages.
    """
    page = ParentalKey('units.UnitPage', related_name='unit_role_placements')
    role = models.ForeignKey('units.Role', related_name='+')

    class Meta:
        verbose_name = 'Unit Placement'
        verbose_name_plural = 'Unit Placements'

    panels = [
        SnippetChooserPanel('role'),
    ]

    def __str__(self):
        return self.page.title + ' -> ' + self.role.text


class UnitPagePhoneNumbers(Orderable, PhoneNumber):
    """
    Create a through table for linking phone numbers 
    to UnitPage content types.
    """
    page = ParentalKey('units.UnitPage', related_name='phone_numbers')


class UnitPageReports(Orderable, Report):
    """
    Reports for unit pages.
    """
    page = ParentalKey('units.UnitPage', related_name='unit_reports')


class UnitPage(BasePage, FaxNumber):
    """
    Basic structure for units and departments.
    """
    display_in_directory = models.BooleanField(default=True)
    email = models.EmailField(max_length=254, blank=True)
    contact_url = models.URLField(max_length=200, blank=True, default='')
    room_number = models.CharField(max_length=32, blank=True)
    public_web_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    location = models.ForeignKey(
        'public.LocationPage',
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        related_name='%(app_label)s_%(class)s_related'
    )
    body = StreamField(DefaultBodyFields())

    content_panels = Page.content_panels + [
        FieldPanel('display_in_directory'),
        InlinePanel('unit_role_placements', label='Role'),
        InlinePanel('phone_numbers', label='Phone Numbers'),
        MultiFieldPanel(
            [
                FieldPanel('email'),
                FieldPanel('contact_url'),
            ],
            heading="Online Contact Information",
        ),
        MultiFieldPanel(
            [
                FieldPanel('fax_number'),
            ],
            heading='Fax Number'
        ),
        FieldPanel('location'), 
        PageChooserPanel('public_web_page'),
        InlinePanel('unit_reports', label='Reports'),
        StreamFieldPanel('body'),
    ] + BasePage.content_panels

    search_fields = Page.search_fields + (
        index.SearchField('body'),
    )

    subpage_types = ['public.StandardPage', 'public.LocationPage']

    def get_full_name(self):
        chunks = []
        unit = self
        while True:
            if unit == None:
                break
            if not isinstance(unit.specific_class(), UnitPage):
                break
            chunks.append(unit.title)
            unit = unit.get_parent()
        return ' - '.join(list(reversed(chunks)))


class UnitIndexPage(BasePage):
    intro = RichTextField()
   
    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ] + BasePage.content_panels
   
    subpage_types = ['units.UnitPage']
