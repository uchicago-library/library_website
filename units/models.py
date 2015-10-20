from django.db import models
from library_website.settings.base import PHONE_FORMAT, PHONE_ERROR_MSG
from wagtail.wagtailcore.models import Orderable, Page
from wagtail.wagtailadmin.edit_handlers import FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel, PageChooserPanel
from wagtail.wagtailsearch import index
from wagtail.wagtailsnippets.models import register_snippet
from wagtail.wagtailsnippets.edit_handlers import SnippetChooserPanel
from modelcluster.fields import ParentalKey
from django.core.validators import RegexValidator
from base.models import BasePage

@register_snippet
class Role(models.Model, index.Indexed):
    """
    Snippet for roles.
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


class PhoneNumber(models.Model):
    """
    Abstract phone number type.
    """
    label = models.CharField(max_length=25)
    phone_regex = RegexValidator(regex=PHONE_FORMAT, message=PHONE_ERROR_MSG)
    number = models.CharField(validators=[phone_regex], max_length=12)

    panels = [
        FieldRowPanel([
            FieldPanel('label', classname='col6'),
            FieldPanel('number', classname='col6'),
        ])
    ]

    class Meta:
        abstract = True


class UnitPagePhoneNumbers(Orderable, PhoneNumber):
    """
    Create a through table for linking phone numbers 
    to UnitPage content types.
    """
    page = ParentalKey('units.UnitPage', related_name='phone_numbers')


class FaxNumber(models.Model):
    """
    Abstract phone number type.
    """
    phone_regex = RegexValidator(regex=PHONE_FORMAT, message=PHONE_ERROR_MSG)
    number = models.CharField(validators=[phone_regex], max_length=12)

    panels = [
        FieldPanel('number'),
    ]

    class Meta:
        abstract = True


class UnitPageFaxNumbers(Orderable, FaxNumber):
    """
    Create a through table for linking fax numbers 
    to UnitPage content types.
    """
    page = ParentalKey('units.UnitPage', related_name='fax_numbers')


class UnitPage(BasePage):
    """
    Basic structure for units and departments.
    """
    display_in_directory = models.BooleanField(default=False)
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
        InlinePanel('fax_numbers', label='Fax Numbers'),
        FieldPanel('location'), # Needs to swap with unit in the abstract class
        PageChooserPanel('public_web_page'),
    ]
