from base.models import LinkFields
from django.db import models
from wagtail.wagtailcore.models import Orderable, Page
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel, PageChooserPanel, MultiFieldPanel
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsearch import index
from wagtail.wagtailsnippets.models import register_snippet
from wagtail.wagtailsnippets.edit_handlers import SnippetChooserPanel
from modelcluster.fields import ParentalKey
from base.models import PublicBasePage
from public.models import DonorPage, LocationPage
from staff.models import StaffPage, StaffPageSubjectPlacement
from subjects.models import Subject

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


class CollectionPageSubjectPlacement(Orderable, models.Model):
    page = ParentalKey('lib_collections.CollectionPage', related_name='collection_subject_placements')
    subject = models.ForeignKey('subjects.Subject', related_name='collection_pages')

    class Meta:
        verbose_name = "Subject Placement"
        verbose_name_plural = "Subbject Placements"

    panels = [
        SnippetChooserPanel('subject'),
    ]

    def __str__(self):
        return self.page.title + " -> " + self.subject.name


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

# Interstitial model for linking the collection RelatedPages to the CollectionPage
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
class CollectionPage(PublicBasePage):
    """
    Pages for individual collections.
    """
    acknowledgments = models.TextField(null=False, blank=True, default='')
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

    subpage_types = []

    content_panels = Page.content_panels + [
        FieldPanel('acknowledgments'),
        InlinePanel('alternate_name', label='Alternate Names'),
        FieldPanel('short_abstract'),
        FieldPanel('full_description'),
        ImageChooserPanel('thumbnail'),
        InlinePanel('collection_subject_placements', label='Subjects'),
        InlinePanel('collection_placements', label='Formats'),
        FieldPanel('access_instructions'),
        InlinePanel('access_links', label='Access Links (Top link is primary)'),
        InlinePanel('related_collection_placement', label='Related Collection'),
        FieldPanel('collection_location'),
        InlinePanel('donor_page_list_placement', label='Donor'),
        FieldPanel('staff_contact'),
    ] + PublicBasePage.content_panels

    search_fields = PublicBasePage.search_fields + (
        index.FilterField('text'),
        index.FilterField('title'),
        index.SearchField('short_abstract'),
        index.SearchField('full_description'),
        index.SearchField('thumbnail'),
        index.SearchField('access_instructions'),
        index.SearchField('collection_location'),
        index.SearchField('staff_contact'),
    )


class SubjectSpecialistPlacement(Orderable, models.Model):
    """
    Creates a through table that connects StaffPage objects to
    the CollectionAreaPages as subject specialists .
    """
    parent = ParentalKey(
        'lib_collections.CollectingAreaPage',
        related_name='subject_specialist_placement',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    subject_specialist = models.ForeignKey(
        'staff.StaffPage',
        related_name='subject_specialist',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )


class StacksRange(models.Model):
    """
    Abstract model for call number ranges.
    """
    stacks_range = models.CharField(max_length=100, blank=True) 
    stacks_URL = models.URLField(max_length=254, blank=True, default='')

    panels = [
        FieldPanel('stacks_range'),
        FieldPanel('stacks_URL'),
    ]

    class Meta:
        abstract = True


class CollectingAreaPageStacksRanges(Orderable, StacksRange):
    """
    Create a through table for call number stacks ranges
    linked to the CollectingAreaPages.
    """
    page = ParentalKey('lib_collections.CollectingAreaPage', related_name='stacks_ranges')


class CollectingAreaReferenceLocationPlacement(Orderable, models.Model):
    """
    Through table for repeatable reference locations in the
    CollectingAreaPage content type.
    """
    parent = ParentalKey(
        'lib_collections.CollectingAreaPage',
        related_name='reference_location_placements',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    related_collection = models.ForeignKey(
        'public.LocationPage',
        related_name='reference_location',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )


class HighlightedCollectionsPlacement(Orderable, models.Model):
    """
    Through table for repeatable highlighted collections
    in the CollectingAreaPage content type.
    """
    parent = ParentalKey(
        'lib_collections.CollectingAreaPage', 
        related_name='highlighted_collection_placements', 
        null=True, 
        blank=False, 
        on_delete=models.SET_NULL
    )

    collection = models.ForeignKey(
        'CollectionPage', 
        related_name='highlighted_collections', 
        null=True, 
        blank=False, 
        on_delete=models.SET_NULL
    )


class RegionalCollection(models.Model):
    """
    Abstract model for regional collections.
    """
    collection_name = models.CharField(max_length=254, blank=True) 
    collection_description =  models.TextField(blank=True)

    panels = [
        FieldPanel('collection_name'),
        FieldPanel('collection_description'),
    ]

    class Meta:
        abstract = True


class RegionalCollectionPlacements(Orderable, RegionalCollection):
    """
    Through table for repeatable regional collection fields.
    """
    page = ParentalKey('lib_collections.CollectingAreaPage', related_name='regional_collections')



class LibGuide(models.Model):
    """
    Abstract model for lib guides.
    """
    guide_link_text = models.CharField(max_length=255, blank=False, default='')
    guide_link_url = models.URLField("Libguide URL", blank=False, default='')

    panels = [
        FieldPanel('guide_link_text'),
        FieldPanel('guide_link_url'),
    ]

    class Meta:
        abstract = True


class CollectingAreaPageLibGuides(Orderable, LibGuide):
    """
    Through table for repeatable "Other guides".
    """
    page = ParentalKey('lib_collections.CollectingAreaPage', related_name='lib_guides')


class CollectingAreaPage(PublicBasePage, LibGuide):
    """
    Content type for collecting area pages.
    """
    subject = models.ForeignKey(
        'subjects.Subject',
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name='%(app_label)s_%(class)s_related'
    )
    collecting_statement = models.TextField(null=False, blank=False)
    
    subpage_types = []

    content_panels = Page.content_panels + [
        FieldPanel('subject'),
        FieldPanel('collecting_statement'),
        InlinePanel('subject_specialist_placement', label='Subject Specialist'),
        InlinePanel('stacks_ranges', label='Stacks Ranges'),
        InlinePanel('reference_location_placements', label='Reference Locations'),
        InlinePanel('highlighted_collection_placements', label='Highlighted Collections'),
        InlinePanel('regional_collections', label='Regional Collections'),
        MultiFieldPanel(
            [
                FieldPanel('guide_link_text'),
                FieldPanel('guide_link_url'),
            ],
            heading='Primary Guide'
        ),
        InlinePanel('lib_guides', label='Other Guides'),
    ] + PublicBasePage.content_panels

    search_fields = PublicBasePage.search_fields + (
        index.SearchField('subject'),
        index.SearchField('collecting_statement'),
        index.SearchField('guide_link_text'),
        index.SearchField('guide_link_url'),
    )


class ExhibitPageSubjectPlacement(Orderable, models.Model):
    page = ParentalKey('lib_collections.ExhibitPage', related_name='exhibit_subject_placements')
    subject = models.ForeignKey('subjects.Subject', related_name='exhibit_pages')

    class Meta:
        verbose_name = "Subject Placement"
        verbose_name_plural = "Subbject Placements"

    panels = [
        SnippetChooserPanel('subject'),
    ]

    def __str__(self):
        return self.page.title + " -> " + self.subject.name


# Interstitial model for linking ExhibitPages to related CollectionPages
class ExhibitPageRelatedCollectionPagePlacement(Orderable, models.Model):
    """
    Creates a through table to attach related CollectionPages to
    the ExhibitPage type. 
    """
    parent = ParentalKey(
        'lib_collections.ExhibitPage', 
        related_name='exhibit_page_related_collection_placement', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL
    )

    related_collection = models.ForeignKey(
        'CollectionPage', 
        related_name='exhibit_page_related_collection', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL
    )


# Interstitial model for linking the DonorPages to the ExhibitPage
class ExhibitPageDonorPagePlacement(Orderable, models.Model):
    """
    Create a through table for linking donor pages to exhibit pages
    """
    parent = ParentalKey(
        'lib_collections.ExhibitPage', 
        related_name='exhibit_page_donor_page_list_placement', 
        null=True, 
        blank=False, 
        on_delete=models.SET_NULL
    )

    donor = models.ForeignKey(
        'public.DonorPage', 
        related_name='exhibit_page_donor_page', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL
    )


class ExhibitPage(PublicBasePage):
    """
    Pages for individual exhibits.
    """
    acknowledgments = models.TextField(null=False, blank=True, default='')
    short_abstract = models.TextField(null=False, blank=False, default='')
    full_description = models.TextField(null=False, blank=False, default='')
    thumbnail = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    ) 
    thumbnail_caption = models.TextField(null=False, blank=True, default='')
    staff_contact = models.ForeignKey('staff.StaffPage',
        null=True, blank=True, on_delete=models.SET_NULL)
    student_exhibit = models.BooleanField(default=False)

    exhibit_open_date = models.DateField(blank=True, null=True)
    exhibit_close_date = models.DateField(blank=True, null=True)
    exhibit_location = models.ForeignKey('public.LocationPage',
        null=True, blank=True, on_delete=models.SET_NULL)
    exhibit_daily_hours = models.CharField(blank=True, null=False, default='', max_length=255)
    exhibit_cost = models.CharField(blank=True, null=False, default='', max_length=255)
    space_type = models.CharField(null=False, blank=True, choices=(('Case', 'Case'), ('Gallery', 'Gallery')), max_length=255)
    web_exhibit_url = models.URLField("Web Exhibit URL", blank=True)
    publication_description = models.CharField(null=False, blank=True, default='', max_length=255)
    publication_price = models.CharField(null=False, blank=True, default='', max_length=255)
    publication_url = models.URLField("Publication URL", blank=True)
    ordering_information = models.BooleanField(default=False)

    exhibit_text_link_external = models.URLField("Exhibit text external link", blank=True)
    exhibit_text_link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL
    )
    exhibit_text_document = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL
    )
    
    exhibit_checklist_link_external = models.URLField("Exhibit checklist external link", blank=True)
    exhibit_checklist_link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL
    )
    exhibit_checklist_document = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL
    )

    subpage_types = []

    content_panels = Page.content_panels + [
        FieldPanel('acknowledgments'),
        FieldPanel('short_abstract'),
        FieldPanel('full_description'),
        MultiFieldPanel(
            [
                ImageChooserPanel('thumbnail'),
                FieldPanel('thumbnail_caption')
            ],
            heading='Thumbnail'
        ),
        InlinePanel('exhibit_subject_placements', label='Subjects'),
        InlinePanel('exhibit_page_related_collection_placement', label='Related Collection'),
        InlinePanel('exhibit_page_donor_page_list_placement', label='Donor'),
        FieldPanel('student_exhibit'),
        FieldPanel('exhibit_open_date'),
        FieldPanel('exhibit_close_date'),
        FieldPanel('exhibit_location'),
        FieldPanel('exhibit_daily_hours'),
        FieldPanel('exhibit_cost'),
        FieldPanel('space_type'),
        FieldPanel('web_exhibit_url'),
        FieldPanel('publication_description'),
        FieldPanel('publication_price'),
        FieldPanel('publication_url'),
        FieldPanel('ordering_information'),
        MultiFieldPanel(
            [
                FieldPanel('exhibit_text_link_external'),
                PageChooserPanel('exhibit_text_link_page'),
                DocumentChooserPanel('exhibit_text_document')
            ],
            heading='Exhibit Text (Choose One or None)'
        ),
        MultiFieldPanel(
            [
                FieldPanel('exhibit_checklist_link_external'),
                PageChooserPanel('exhibit_checklist_link_page'),
                DocumentChooserPanel('exhibit_checklist_document')
            ],
            heading='Exhibit Checklist (Choose One or None)'
        ),
        FieldPanel('staff_contact'),
    ] + PublicBasePage.content_panels

    search_fields = PublicBasePage.search_fields + (
        index.FilterField('exhibit_open_date'),
        index.FilterField('exhibit_close_date'),
        index.FilterField('subject_id'),
        index.FilterField('title'),
        index.FilterField('web_exhibit_url'),
        index.SearchField('short_abstract'),
        index.SearchField('full_description'),
        index.SearchField('thumbnail'),
        index.SearchField('thumbnail_caption'),
        index.SearchField('exhibit_location'),
        index.SearchField('exhibit_daily_hours'),
        index.SearchField('exhibit_cost'),
        index.SearchField('space_type'),
        index.SearchField('web_exhibit_url'),
        index.SearchField('publication_description'),
        index.SearchField('publication_price'),
        index.SearchField('publication_url'),
        index.SearchField('staff_contact'),
    )


