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
from base.models import BasePage, ContactFields, DefaultBodyFields

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


class UnitPage(BasePage, ContactFields):
    """
    Basic structure for units and departments.
    """
    contact_point_title = models.CharField(max_length=255, blank=True)
    friendly_name = models.CharField(max_length=255, blank=True)
    display_in_directory = models.BooleanField(default=True)
    display_in_dropdown = models.BooleanField(default=False)
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
    directory_unit = models.ForeignKey(
        'directory_unit.DirectoryUnit',
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        related_name='%(app_label)s_%(class)s_related'
    )

    content_panels = Page.content_panels + [
        FieldPanel('contact_point_title'),
        FieldPanel('friendly_name'),
        FieldPanel('display_in_directory'),
        FieldPanel('display_in_dropdown'),
        FieldPanel('room_number'),
        InlinePanel('unit_role_placements', label='Role'),
        PageChooserPanel('public_web_page'),
        FieldPanel('location'), 
        FieldPanel('directory_unit'), 
    ] + BasePage.content_panels + ContactFields.content_panels

    subpage_types = []

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

    class Meta:
        ordering = ['title']


class UnitIndexPage(BasePage):
    intro = RichTextField()
   
    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ] + BasePage.content_panels

    search_fields = BasePage.search_fields + (
        index.SearchField('intro'),
    )
   
    subpage_types = ['units.UnitPage']

    def get_context(self, request):
        context = super(UnitIndexPage, self).get_context(request)

        context['units_hierarchical'] = []
        for u in UnitPage.objects.filter(display_in_directory = True):
            unit_page = {} 
            if u.contact_point_title:
                unit_page['full_name'] = u.directory_unit.fullName + ' - ' + u.contact_point_title
            else:
                unit_page['full_name'] = u.directory_unit.fullName
            context['units_hierarchical'].append(unit_page)

        return context
            
