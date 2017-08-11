from base.models import DefaultBodyFields, LinkFields
from django.db import models
from django.core.validators import RegexValidator
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailcore.models import Orderable, Page, Site
from wagtail.wagtailadmin.edit_handlers import TabbedInterface, ObjectList, FieldPanel, FieldRowPanel, InlinePanel, PageChooserPanel, MultiFieldPanel, StreamFieldPanel
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

DEFAULT_WEB_EXHIBIT_FONT = '"Helvetica Neue", Helvetica, Arial, sans-serif'

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

    subpage_types = ['public.StandardPage']

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
        staff_position_title = ''
        staff_email = ''
        staff_phone_number = ''
        staff_faculty_exchange = ''
        try:
            staff_title = self.staff_contact.title
            staff_position_title = self.staff_contact.position_title
            staff_email = self.staff_contact.staff_page_email.first().email
            staff_phone_number = self.staff_contact.staff_page_phone_faculty_exchange.first().phone_number
            staff_faculty_exchange = self.staff_contact.staff_page_phone_faculty_exchange.first().faculty_exchange
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
                unit_phone_label = self.unit.unit_page_phone_number.first().phone_label
            except:
                pass
            try:
                unit_phone_number = self.unit.unit_page_phone_number.first().phone_number
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
        context['staff_position_title'] = staff_position_title
        context['staff_email'] = staff_email
        context['staff_phone_number'] = staff_phone_number
        context['staff_faculty_exchange'] = staff_faculty_exchange
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


# CollectingArea page models

class RegionalCollection(models.Model):
    """
    Abstract model for regional collections.
    """
    regional_collection_name = models.CharField(max_length=254, blank=True)
    regional_collection_url = models.URLField("Regional Collection URL", blank=True, null=True)
    regional_collection_description = models.TextField(blank=True)

    panels = [
        FieldPanel('regional_collection_name'),
        FieldPanel('regional_collection_url'),
        FieldPanel('regional_collection_description'),
    ]

    class Meta:
        abstract = True


class RegionalCollectionPlacements(Orderable, RegionalCollection):
    """
    Through table for repeatable regional collections.
    """
    page = ParentalKey('lib_collections.CollectingAreaPage', related_name='regional_collections')



class LibGuide(models.Model):
    """
    Abstract model for lib guides.
    """
    guide_link_text = models.CharField(max_length=255, blank=True, null=True)
    guide_link_url = models.URLField("Libguide URL", blank=True, null=True)

    panels = [
        FieldPanel('guide_link_text'),
        FieldPanel('guide_link_url'),
    ]

    class Meta:
        abstract = True


class CollectingAreaPageLibGuides(Orderable, LibGuide):
    """
    Through table for repeatable guides.
    """
    page = ParentalKey('lib_collections.CollectingAreaPage', related_name='lib_guides')


# Collecting Area page content type
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
    collecting_statement = StreamField(DefaultBodyFields(), blank=False, null=True)
    policy_link_text = models.CharField(max_length=255, blank=True, null=True)
    policy_link_url = models.URLField("Policy URL", blank=True, null=True)
    short_abstract = models.TextField(null=True, blank=True)
    thumbnail = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    collection_location = models.ForeignKey('public.LocationPage',
        null=True, blank=True, on_delete=models.SET_NULL)
    reference_materials = RichTextField(blank=True, null=True)
    circulating_materials = RichTextField(blank=True, null=True)
    archival_link_text = models.CharField(max_length=255, blank=True, null=True)
    archival_link_url = models.URLField("Archival URL", blank=True, null=True)
    first_feature = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL
    )
    second_feature = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL
    )
    third_feature = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL
    )
    fourth_feature = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL
    )
    supplementary_header = models.CharField(max_length=255, blank=True, null=True)
    supplementary_text = RichTextField(blank=True, null=True)
    related_collecting_area = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL
    )

    subpage_types = []

    content_panels = Page.content_panels + [
        FieldPanel('subject'),
        StreamFieldPanel('collecting_statement'),
        MultiFieldPanel(
            [
                FieldPanel('policy_link_text'),
                FieldPanel('policy_link_url'),
            ],
            heading='Collecting Policy Link',
            classname='collapsible collapsed',
        ),
        FieldPanel('short_abstract'),
        ImageChooserPanel('thumbnail'),
        FieldPanel('collection_location'),
        InlinePanel('lib_guides', label='Subject Guides'),
        MultiFieldPanel(
            [
                FieldPanel('reference_materials'),
                FieldPanel('circulating_materials'),
            ],
            heading='Reference and Stacks Materials',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('archival_link_text'),
                FieldPanel('archival_link_url'),
            ],
            heading='Archive Materials',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel([
                PageChooserPanel('first_feature', ['lib_collections.CollectionPage', 'lib_collections.ExhibitPage']),
                PageChooserPanel('second_feature', ['lib_collections.CollectionPage', 'lib_collections.ExhibitPage']),
                PageChooserPanel('third_feature', ['lib_collections.CollectionPage', 'lib_collections.ExhibitPage']),
                PageChooserPanel('fourth_feature', ['lib_collections.CollectionPage', 'lib_collections.ExhibitPage']),
            ],
            heading='Featured Collections and Exhibits',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('supplementary_header'),
                FieldPanel('supplementary_text'),
            ],
            heading='Supplementary Text',
            classname='collapsible collapsed',
        ),
        PageChooserPanel('related_collecting_area', ['lib_collections.CollectingAreaPage']),
        InlinePanel('regional_collections', label='Other Local Collections', help_text='Related collections that are held by other institutions, like BMRC, Newberry, etc.'),
    ] + PublicBasePage.content_panels

    search_fields = PublicBasePage.search_fields + [
        index.SearchField('subject'),
        index.SearchField('collecting_statement'),
        index.SearchField('guide_link_text'),
        index.SearchField('guide_link_url'),
    ]

    def has_right_sidebar(self):
        return True

    def get_subjects(self, children=False):
        """
        Get the subject assigned to this
        CollectingAreaPage.

        Args:
            children: defaults to False.
            If true, get child subjects.

        Return:
            A set of subjects
        """
        if children:
            return set(self.subject.get_descendants())
        return set([self.subject])

    def _build_related_link(self, page_id):
        """
        Args:
            page_id, integer

        Return:
            tuple of strings representing a link to
            a page where the first item in the tuple
            is a page title and the second item is a url.
        """
        current_site = Site.objects.get(is_default_site=True)
        page = Page.objects.get(id=page_id)
        title = str(page)
        url = page.relative_url(current_site)
        return (title, url)

    def _build_subject_specialist(self, librarian):
        """
        Build a data object representing a subject
        specialist.

        Args:
            librarian: StaffPage object.

        Returns:
            Mixed tuple
        """
        current_site = Site.objects.get(is_default_site=True)
        staff_member = str(librarian)
        title = librarian.position_title
        url = librarian.public_page.relative_url(current_site)
        thumb = librarian.profile_picture
        email = librarian.staff_page_email.values_list('email', flat=True).first()
        phone_and_fac = tuple(librarian.staff_page_phone_faculty_exchange.values_list('phone_number', 'faculty_exchange'))
        return (staff_member, title, url, email, phone_and_fac, thumb)


    def get_related(self, children=False):
        """
        Get related exhibits or collections by subject.

        Args:
            children: boolean, show hierarchical subjects.

        Return:
            A dictionary of sets. The dictionary has a
            key for 'collections', 'exhibits', and
            'subject_specialists'. Collection and exhibit
            sets contain tuples of strings where the first
            string is a page title and the second string
            is a relative url. Subject specialist sets
            contain tuples with a slightly more complicated
            structure.
        """
        related = {'collections': set([]),
                   'exhibits': set([])}
        subjects = self.get_subjects(children)
        # Related collections and exhibits
        for subject in subjects:
            related['collections'] = related['collections'] | set(self._build_related_link(page[0]) for page in subject.collection_pages.values_list('page_id'))
            related['exhibits'] = related['exhibits'] | set(self._build_related_link(page[0]) for page in subject.exhibit_pages.values_list('page_id'))

        # Staff pages for subject specialists
        # Can make this more efficient if HR starts using the employee_type field
        librarians = StaffPage.objects.live()
        subject_specialists = set([])
        for staff in librarians:
            intersecting = len(staff.get_subject_objects().intersection(subjects)) > 0
            if intersecting:
                subject_specialists.add(self._build_subject_specialist(staff))
        related['subject_specialists'] = subject_specialists
        return related


    def get_features(self):
        """
        Return a list of tuples representing featured CollectionPages
        or ExhibitPages.

        Return:
            A list of tuples representing featured collections
            and exhibits. Each tupal has four items: 1. string
            representing the page title, 2. string, page url,
            3. string, short description, 4. image object.
        """
        retval = []
        current_site = Site.objects.get(is_default_site=True)
        features = [self.first_feature, self.second_feature, self.third_feature, self.fourth_feature]
        for feature in features:
            if feature:
                retval.append((str(feature), feature.relative_url(current_site), feature.specific.short_abstract, feature.specific.thumbnail))
        return retval

    def get_context(self, request):
        """
        Override the page object's get context method.
        """
        context = super(CollectingAreaPage, self).get_context(request)

        related = self.get_related(False)
        limit = -1
        context['related_collections'] = sorted(related['collections'])[:limit]
        context['related_exhibits'] = sorted(related['exhibits'])[:limit]
        context['related_subject_specialists'] = sorted(related['subject_specialists'])
        context['features'] = self.get_features()
        context['lib_guides'] = self.lib_guides.get_object_list()

        try:
            regional_collections = self.regional_collections.all()
        except(AttributeError):
            regional_collections = []
        context['regional_collections'] = regional_collections
        return context

class ExhibitPageSubjectPlacement(Orderable, models.Model):
    page = ParentalKey('lib_collections.ExhibitPage', related_name='exhibit_subject_placements')
    subject = models.ForeignKey('subjects.Subject', related_name='exhibit_pages')

    class Meta:
        verbose_name = "Subject Placement"
        verbose_name_plural = "Subject Placements"

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

        font = DEFAULT_WEB_EXHIBIT_FONT
        if self.font_family:
            font = self.font_family
 
        context = super(ExhibitPage, self).get_context(request)
        footer_img = self.get_web_exhibit_footer_img(self.location_and_hours['page_location'].id) # must be set after context
        context['default_image'] = default_image
        context['staff_url'] = staff_url
        context['branding_color'] = self.branding_color
        context['font_family'] = font 
        context['google_font_link'] = self.google_font_link
        context['footer_img'] = footer_img
        context['has_exhibit_footer'] = not (not footer_img)
        context['is_web_exhibit'] = self.is_web_exhibit()
        context['related_collections'] = self.get_related_collections(request)
        context['exhibit_open_date'] = self.exhibit_open_date
        context['exhibit_close_date'] = self.exhibit_close_date
        context['exhibit_close_date'] = self.exhibit_location

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

        font = DEFAULT_WEB_EXHIBIT_FONT
        if exhibit.font_family:
            font = exhibit.font_family

        context['branding_color'] = exhibit.branding_color
        context['font_family'] = font
        context['google_font_link'] = exhibit.google_font_link
        context['footer_img'] = footer_img
        context['has_exhibit_footer'] = not (not footer_img)
        context['is_web_exhibit'] = True
        context['related_collections'] = exhibit.get_related_collections(request)
        context['exhibit_open_date'] = exhibit.exhibit_open_date
        context['exhibit_close_date'] = exhibit.exhibit_close_date
        context['exhibit_close_date'] = exhibit.exhibit_location
        return context 
