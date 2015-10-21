from django.db import models
from wagtail.wagtailcore.models import Orderable, Page
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel, PageChooserPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsearch import index
from wagtail.wagtailsnippets.models import register_snippet
from wagtail.wagtailsnippets.edit_handlers import SnippetChooserPanel
from modelcluster.fields import ParentalKey
from base.models import BasePage
from public.models import DonorPage
from staff.models import StaffPage

# The abstract model for related links, complete with panels
class AccessLink(models.Model):
    access_link_label = models.CharField(max_length=255)
    access_link_url = models.URLField("Access link URL", blank=False)

    panels = [
        FieldPanel('access_link_label'),
        FieldPanel('access_link_url'),
    ]

    class Meta:
        abstract = True

# The real model which combines the abstract model, an
# Orderable helper class, and what amounts to a ForeignKey link
# to the model we want to add related links to (CollectionPage)
class CollectionPageAccessLinks(Orderable, AccessLink):
    page = ParentalKey('lib_collections.CollectionPage', related_name='access_links')


# Model for format strings to be used on collection pages
@register_snippet
class Format(models.Model, index.Indexed):
    text = models.CharField(max_length=255, blank=False)

    panels = [
        FieldPanel('text'),
    ]

    def __str__(self):
        return self.text

    search_fields = [
        index.SearchField('text', partial_match=True),
    ]

# Interstitial model for linking the Format model to the CollectionPage
class CollectionPageFormatPlacement(Orderable, models.Model):
    page = ParentalKey('lib_collections.CollectionPage', related_name='collection_placements')
    format = models.ForeignKey('lib_collections.Format', related_name='+')

    class Meta:
        verbose_name = "Collection Placement"
        verbose_name_plural = "Collection Placements"

    panels = [
        SnippetChooserPanel('format'),
    ]

    def __str__(self):
        return self.page.title + " -> " + self.format.text

# Interstitial model for linking the DonorPages to the CollectionPage
class DonorPagePlacement(Orderable, models.Model):
    """
    Create a through table for linking donor pages to collection pages
    """
    parent = ParentalKey(
        'lib_collections.CollectionPage', 
        related_name='donor_page_list_placement', 
        null=True, 
        blank=False, 
        on_delete=models.SET_NULL
    )

    donor = models.ForeignKey(
        'public.DonorPage', 
        related_name='donor_page', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL
    )

# The abstract model for alternative collection names 
class AlternateName(models.Model):
    alternate_name = models.CharField(max_length=255, blank=True)

    panels = [
        FieldPanel('alternate_name'),
    ]

    class Meta:
        abstract = True

# Attaches alternative names to collections.
class CollectionPageAlternateNames(Orderable, AlternateName):
    """
    Creates a through table for alternate names for CollectionPages.
    """
    page = ParentalKey('lib_collections.CollectionPage', related_name='alternate_name')

# Interstitial model for linking the ollection RelatedPages to the CollectionPage
class RelatedCollectionPagePlacement(Orderable, models.Model):
    """
    Creates a through table for RelatedPages that attach to 
    the CollectionPage type. 
    """
    parent = ParentalKey(
        'lib_collections.CollectionPage', 
        related_name='related_collection_placement', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL
    )

    related_collection = models.ForeignKey(
        'CollectionPage', 
        related_name='related_collection', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL
    )

 
# Collection page content type
class CollectionPage(BasePage):
    """
    Pages for individual collections.
    """
    short_abstract = models.TextField(null=False, blank=False, default='')
    full_description = models.TextField(null=False, blank=False, default='')
    access_instructions = models.TextField(null=False, blank=True, default='')
    thumbnail = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    ) 
    collection_location = models.ForeignKey('public.LocationPage',
        null=True, blank=True, on_delete=models.SET_NULL)
    staff_contact = models.ForeignKey('staff.StaffPage',
        null=True, blank=True, on_delete=models.SET_NULL)

    content_panels = Page.content_panels + [
        InlinePanel('alternate_name', label='Alternate Names'),
        FieldPanel('short_abstract'),
        FieldPanel('full_description'),
        ImageChooserPanel('thumbnail'),
        InlinePanel('collection_placements', label='Format'),
        FieldPanel('access_instructions'),
        InlinePanel('access_links', label='Access Links'),
        InlinePanel('related_collection_placement', label='Related Collection'),
        FieldPanel('collection_location'),
        InlinePanel('donor_page_list_placement', label='Donor'),
        FieldPanel('staff_contact'),
        FieldPanel('unit'),
    ]
