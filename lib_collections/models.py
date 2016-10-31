from base.models import DefaultBodyFields, LinkFields
from django.db import models
from django.core.validators import RegexValidator
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailcore.models import Orderable, Page, Site
from wagtail.wagtailadmin.edit_handlers import TabbedInterface, ObjectList, FieldPanel, InlinePanel, PageChooserPanel, MultiFieldPanel, StreamFieldPanel
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel
from wagtail.wagtailimages.models import Image
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsearch import index
from wagtail.wagtailsnippets.models import register_snippet
from wagtail.wagtailsnippets.edit_handlers import SnippetChooserPanel
from modelcluster.fields import ParentalKey
from base.models import PublicBasePage
from public.models import DonorPage, LocationPage, StaffPublicPage
from staff.models import StaffPage, StaffPageSubjectPlacement
from subjects.models import Subject
from library_website.settings import SCRC_BUILDING_ID, CRERAR_BUILDING_ID, CRERAR_EXHIBIT_FOOTER_IMG, SCRC_EXHIBIT_FOOTER_IMG

# The abstract model for related links, complete with panels
class SupplementaryAccessLink(models.Model):
    supplementary_access_link_label = models.CharField(max_length=255)
    supplementary_access_link_url = models.URLField("Supplementary access link URL", blank=False)

    panels = [
        FieldPanel('supplementary_access_link_label'),
        FieldPanel('supplementary_access_link_url'),
    ]

    class Meta:
        abstract = True

# The real model which combines the abstract model, an
# Orderable helper class, and what amounts to a ForeignKey link
# to the model we want to add related links to (CollectionPage)
class CollectionPageSupplementaryAccessLinks(Orderable, SupplementaryAccessLink):
    page = ParentalKey('lib_collections.CollectionPage', related_name='supplementary_access_links')


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
    full_description = StreamField(DefaultBodyFields(), blank=True, null=True)
    access_instructions = models.TextField(null=False, blank=True, default='')
    thumbnail = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    thumbnail_caption = models.TextField(null=False, blank=True) 
    primary_online_access_link_label = models.CharField(max_length=255, blank=True)
    primary_online_access_link_url = models.URLField("Primary online access link URL", blank=True)
    collection_location = models.ForeignKey('public.LocationPage',
        null=True, blank=True, on_delete=models.SET_NULL)
    staff_contact = models.ForeignKey('staff.StaffPage',
        null=True, blank=True, on_delete=models.SET_NULL)
    unit_contact = models.BooleanField(default=False)

    subpage_types = []

    content_panels = Page.content_panels + [
        FieldPanel('acknowledgments'),
        InlinePanel('alternate_name', label='Alternate Names'),
        FieldPanel('short_abstract'),
        StreamFieldPanel('full_description'),
        MultiFieldPanel(
            [
                ImageChooserPanel('thumbnail'),
                FieldPanel('thumbnail_caption'),
            ],
            heading='Thumbnail'
        ),
        InlinePanel('collection_subject_placements', label='Subjects'),
        InlinePanel('collection_placements', label='Formats'),
        FieldPanel('access_instructions'),
        MultiFieldPanel(
            [
                FieldPanel('primary_online_access_link_label'),
                FieldPanel('primary_online_access_link_url'),
            ],
            heading='Primary Online Access Link'
        ),
        InlinePanel('supplementary_access_links', label='Supplementary Access Links'),
        InlinePanel('related_collection_placement', label='Related Collection'),
        FieldPanel('collection_location'),
        InlinePanel('donor_page_list_placement', label='Donor'),
        MultiFieldPanel(
            [
                FieldPanel('staff_contact'),
                FieldPanel('unit_contact')
            ],
            heading='Staff or Unit Contact'
        )
    ] + PublicBasePage.content_panels

    search_fields = PublicBasePage.search_fields + [
        index.FilterField('title'),
        index.SearchField('short_abstract'),
        index.SearchField('full_description'),
        index.SearchField('thumbnail'),
        index.SearchField('thumbnail_caption'),
        index.SearchField('access_instructions'),
        index.SearchField('collection_location'),
        index.SearchField('staff_contact'),
    ]

    def get_context(self, request):
        staff_title = '' 
        staff_vcard_title = ''
        staff_vcard_email = ''
        staff_vcard_phone_number = ''
        staff_vcard_faculty_exchange = ''
        try:
            staff_title = self.staff_contact.title
            staff_vcard_title = self.staff_contact.vcards.first().title
            staff_vcard_email = self.staff_contact.vcards.first().email
            staff_vcard_phone_number = self.staff_contact.vcards.first().phone_number
            staff_vcard_faculty_exchange = self.staff_contact.vcards.first().faculty_exchange
        except:
            pass

        staff_url = ''
        try:
            staff_url = StaffPublicPage.objects.get(cnetid=self.staff_contact.cnetid).url
        except:
            pass

        unit_title = ''
        unit_url = ''
        unit_email_label = ''
        unit_email = ''
        unit_phone_label = ''
        unit_phone_number = ''
        unit_fax_number = ''
        unit_link_text = ''
        unit_link_external = ''
        unit_link_page = ''
        unit_link_document = ''
        if self.unit_contact:
            try:
                unit_title = self.unit.title
            except:
                pass

            try:
                unit_url = self.unit.public_web_page.url
            except:
                pass

            try:
                unit_email_label = self.unit.email_label
            except:
                pass
            try:
                unit_email = self.unit.email
            except:
                pass

            try:
                unit_phone_label = self.unit.phone_label
            except:
                pass
            try:
                unit_phone_number = self.unit.phone_number
            except:
                pass

            try:
                unit_fax_number = self.unit.fax_number
            except:
                pass

            try:
                unit_link_text = self.unit.link_text
            except:
                pass

            try:
                unit_link_external = self.unit.link_external
            except:
                pass

            try:
                unit_link_page = self.unit.link_page.url
            except:
                pass

            try:
                unit_link_document = self.unit.link_document.file.url
            except:
                pass

        default_image = None
        default_image = Image.objects.get(title="Default Placeholder Photo")

        context = super(CollectionPage, self).get_context(request)
        context['default_image'] = default_image
        context['staff_title'] = staff_title
        context['staff_url'] = staff_url
        context['staff_vcard_title'] = staff_vcard_title
        context['staff_vcard_email'] = staff_vcard_email
        context['staff_vcard_phone_number'] = staff_vcard_phone_number
        context['staff_vcard_faculty_exchange'] = staff_vcard_faculty_exchange
        context['unit_title'] = unit_title
        context['unit_url'] = unit_url
        context['unit_email_label'] = unit_email_label
        context['unit_email'] = unit_email
        context['unit_phone_label'] = unit_phone_label
        context['unit_phone_number'] = unit_phone_number
        context['unit_fax_number'] = unit_fax_number
        context['unit_link_text'] = unit_link_text
        context['unit_link_external'] = unit_link_external
        context['unit_link_page'] = unit_link_page
        context['unit_link_document'] = unit_link_document
        context['supplementary_access_links'] = self.supplementary_access_links.get_object_list()
        return context

    def has_right_sidebar(self):
        return True

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

    search_fields = PublicBasePage.search_fields + [
        index.SearchField('subject'),
        index.SearchField('collecting_statement'),
        index.SearchField('guide_link_text'),
        index.SearchField('guide_link_url'),
    ]


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
    full_description = StreamField(DefaultBodyFields(), blank=True, null=True)
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
    unit_contact = models.BooleanField(default=False)
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

    # Web exhibit fields
    web_exhibit = models.BooleanField(default=False, help_text='Display as web exhibit')
    hex_regex = RegexValidator(regex='^#[a-zA-Z0-9]{6}$', \
        message='Please enter a hex color, e.g. #012043')
    branding_color= models.CharField(validators=[hex_regex], max_length=7, blank=True)
    google_font_link = models.URLField(blank=True, 
        help_text='Google fonts link to embedd in the header')
    font_family = models.CharField(max_length=100, blank=True, 
        help_text='CSS font-family value, e.g. \'Roboto\', sans-serif')

    subpage_types = ['lib_collections.ExhibitChildPage']


    web_exhibit_panels = [
        FieldPanel('web_exhibit'),
        MultiFieldPanel(
            [
                ImageChooserPanel('banner_image'),
                ImageChooserPanel('banner_feature'),
                FieldPanel('banner_title'),
                FieldPanel('banner_subtitle'),
            ],
            heading='Banner'
        ),
        MultiFieldPanel(
            [
                FieldPanel('branding_color'),
                FieldPanel('google_font_link'),
                FieldPanel('font_family'),
            ],
            heading='Branding'
        ),
    ]


    content_panels = Page.content_panels + [
        FieldPanel('acknowledgments'),
        FieldPanel('short_abstract'),
        StreamFieldPanel('full_description'),
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
        MultiFieldPanel(
            [
                FieldPanel('exhibit_open_date'),
                FieldPanel('exhibit_close_date'),
            ],
            heading='Dates'
        ),
        MultiFieldPanel(
            [
                FieldPanel('exhibit_location'),
                FieldPanel('exhibit_daily_hours'),
                FieldPanel('exhibit_cost'),
                FieldPanel('space_type'),
            ],
            heading='Visiting information'
        ),
       MultiFieldPanel(
            [
                FieldPanel('web_exhibit_url'),
                FieldPanel('publication_description'),
                FieldPanel('publication_price'),
                FieldPanel('publication_url'),
                FieldPanel('ordering_information'),
            ],
            heading='Publication information'
        ),
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
        MultiFieldPanel(
            [
                FieldPanel('staff_contact'),
                FieldPanel('unit_contact')
            ],
            heading='Staff or Unit Contact'
        )
    ] + PublicBasePage.content_panels

    search_fields = PublicBasePage.search_fields + [
        index.FilterField('exhibit_open_date'),
        index.FilterField('exhibit_close_date'),
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
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(PublicBasePage.promote_panels, heading='Promote'),
        ObjectList(Page.settings_panels, heading='Settings', classname="settings"),
        ObjectList(web_exhibit_panels, heading='Web Exhibit'),
    ])


    def is_web_exhibit(self):
        """
        Determine if an ExhibitPage is a 
        web exhibit.
        """
        return self.web_exhibit

    def has_right_sidebar(self):
        """
        Always has a right sidebar?
        """
        return True

    def get_web_exhibit_footer_img(self, building):
        """
        Get the web exhibit footer image
        for a specific building.

        Returns:
            Image object or None
        """
        #building = self.location_and_hours['page_location'].id
        img = {SCRC_BUILDING_ID: SCRC_EXHIBIT_FOOTER_IMG,
               CRERAR_BUILDING_ID: CRERAR_EXHIBIT_FOOTER_IMG}
        if building in img:
            return Image.objects.get(id=img[building])
        return None

    def get_related_collections(self, request):
        """
        Get the related collections for a web exhibit.
    
        Args:
            request: object

        Returns:
            A list of tuples where the first item in 
            the tuple is a collection title and the
            second item is a url. If no related 
            collections are found, returns None.
        """
        current_site = Site.find_for_request(request)
        collections = self.exhibit_page_related_collection_placement.all() 
        related_collections = '<ul>'
        if collections:
            for collection in collections:
                if collection.related_collection:
                    related_collections += '<li><a href="' + collection.related_collection.relative_url(current_site) + '">' + collection.related_collection.title + '</a></li>'
            return related_collections + '</ul>'
        return None

    def get_context(self, request):
        staff_url = ''
        try:
            staff_url = StaffPublicPage.objects.get(cnetid=self.staff_contact.cnetid).url
        except:
            pass
        default_image = None
        default_image = Image.objects.get(title="Default Placeholder Photo")
 
        context = super(ExhibitPage, self).get_context(request)
        footer_img = self.get_web_exhibit_footer_img(self.location_and_hours['page_location'].id) # must be set after context
        context['default_image'] = default_image
        context['staff_url'] = staff_url
        context['branding_color'] = self.branding_color
        context['font_family'] = self.font_family if self.font_family else '"Helvetica Neue", Helvetica, Arial, sans-serif'
        context['google_font_link'] = self.google_font_link
        context['footer_img'] = footer_img
        context['has_exhibit_footer'] = not (not footer_img)
        context['is_web_exhibit'] = self.is_web_exhibit()
        context['related_collections'] = self.get_related_collections(request)

        return context


class ExhibitChildPage(PublicBasePage):
    """
    Pages for web exhibit child pages.
    """

    body = StreamField(DefaultBodyFields(), blank=True)

    subpage_types = ['lib_collections.ExhibitChildPage']

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
    ] + PublicBasePage.content_panels

    search_fields = PublicBasePage.search_fields + [
        index.SearchField('body'),
    ]

    def get_context(self, request):
        context = super(ExhibitChildPage, self).get_context(request)
        exhibit = self.get_parent_of_type('exhibit page')
        footer_img = exhibit.get_web_exhibit_footer_img(self.location_and_hours['page_location'].id)
        context['branding_color'] = exhibit.branding_color
        context['font_family'] = exhibit.font_family
        context['google_font_link'] = exhibit.google_font_link
        context['footer_img'] = footer_img
        context['has_exhibit_footer'] = not (not footer_img)
        context['is_web_exhibit'] = True
        context['related_collections'] = exhibit.get_related_collections(request)
        return context 
