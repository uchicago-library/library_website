import datetime

import simplejson
import requests
from base.models import DefaultBodyFields, PublicBasePage
from collections import OrderedDict
from diablo_utils import lazy_dotchain
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.core.validators import RegexValidator
from django.db import models
from django.http import Http404, HttpResponse
from django.template.response import TemplateResponse
from django.utils.text import slugify
from library_website.settings import (
    CRERAR_BUILDING_ID, CRERAR_EXHIBIT_FOOTER_IMG, SCRC_BUILDING_ID,
    SCRC_EXHIBIT_FOOTER_IMG, APA_PATH, CHICAGO_PATH, MLA_PATH,
    COLLECTION_OBJECT_TRUNCATE
)
from modelcluster.fields import ParentalKey
from public.models import StaffPublicPage
from staff.models import StaffPage
from wagtail.admin.edit_handlers import (
    FieldPanel, InlinePanel, MultiFieldPanel, ObjectList, PageChooserPanel,
    StreamFieldPanel, TabbedInterface
)
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Orderable, Page, Site
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images.models import Image
from wagtail.search import index
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.snippets.models import register_snippet

from .marklogic import get_record_for_display, get_record_no_parsing
from .utils import (CBrowseURL,
                    CitationInfo,
                    DisplayBrowse,
                    LBrowseURL,
                    IIIFDisplay,
                    )

DEFAULT_WEB_EXHIBIT_FONT = '"Helvetica Neue", Helvetica, Arial, sans-serif'


def get_current_exhibits():
    """
    Get a listing of current exhibits.

    Returns:
        PageQuerySet
    """
    exhibits = ExhibitPage.objects.live()
    current_exhibits = exhibits.filter(
        exhibit_open_date__lt=datetime.datetime.now().date(),
        exhibit_close_date__gt=datetime.datetime.now().date()
    ).distinct()
    return current_exhibits


# The abstract model for related links, complete with panels


class SupplementaryAccessLink(models.Model):
    supplementary_access_link_label = models.CharField(max_length=255)
    supplementary_access_link_url = models.URLField(
        "Supplementary access link URL", blank=False
    )

    panels = [
        FieldPanel('supplementary_access_link_label'),
        FieldPanel('supplementary_access_link_url'),
    ]

    class Meta:
        abstract = True


# The real model which combines the abstract model, an
# Orderable helper class, and what amounts to a ForeignKey link
# to the model we want to add related links to (CollectionPage)


class CollectionPageSupplementaryAccessLinks(
    Orderable, SupplementaryAccessLink
):
    page = ParentalKey(
        'lib_collections.CollectionPage',
        related_name='supplementary_access_links'
    )


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
    page = ParentalKey(
        'lib_collections.CollectionPage',
        on_delete=models.CASCADE,
        related_name='collection_placements'
    )
    format = models.ForeignKey(
        'lib_collections.Format', on_delete=models.CASCADE, related_name='+'
    )

    class Meta:
        verbose_name = "Collection Placement"
        verbose_name_plural = "Collection Placements"

    panels = [
        SnippetChooserPanel('format'),
    ]

    def __str__(self):
        return self.page.title + " -> " + self.format.text


class CollectionPageSubjectPlacement(Orderable, models.Model):
    page = ParentalKey(
        'lib_collections.CollectionPage',
        on_delete=models.CASCADE,
        related_name='collection_subject_placements'
    )
    subject = models.ForeignKey(
        'subjects.Subject',
        on_delete=models.CASCADE,
        related_name='collection_pages'
    )

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
    page = ParentalKey(
        'lib_collections.CollectionPage', related_name='alternate_name'
    )


# Interstitial model for linking the collection RelatedPages to the
# CollectionPage


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


class ExternalService(models.Model):
    """
    Class for link to an external service in a Collection Page.
    """
    MENU_OPTIONS = [
        (1, "LUNA"),
        (2, "BTAA"),
    ]
    service = models.IntegerField(
        choices=MENU_OPTIONS, default=1, help_text='Choose an external service'
    )
    identifier = models.CharField(
        max_length=255, help_text="identifier to retrieve object from service"
    )

    panels = [
        FieldPanel('service'),
        FieldPanel('identifier'),
    ]

    class Meta:
        abstract = True


class CollectionPageExternalService(Orderable, ExternalService):
    """
    Intermediate class for links to external services in a Collection
    Page. (needed to create an InlinePanel)
    """
    page = ParentalKey(
        'lib_collections.CollectionPage', related_name="col_external_service"
    )


class ObjectMetadata(models.Model):
    """
    Class for metadata fields to display in search results.
    """
    MENU_OPTIONS = [
        (1, "go to a results page for the selected item"),
        (2, "link to a related item in the collection"),
    ]
    edm_field_label = models.CharField(max_length=255, blank=True)
    multiple_values = models.BooleanField(
        default=False, help_text='Are there multiple values within the field?'
    )
    hotlinked = models.BooleanField(
        default=False,
        help_text='Do you want this label to linked to a unique browse view?'
    )
    link_target = models.IntegerField(
        choices=MENU_OPTIONS,
        default=1,
        help_text=(
            'How do you want the link to behave? \
            (Required for hotlinked)'
        )
    )

    panels = [
        FieldPanel('edm_field_label'),
        FieldPanel('hotlinked'),
        FieldPanel('multiple_values'),
        FieldPanel('link_target'),
    ]

    class Meta:
        abstract = True


class CollectionPageObjectMetadata(Orderable, ObjectMetadata):
    """
    Intermediate class for metadata fields within a Collection Page
    result.  (needed to create an InlinePanel)
    """
    page = ParentalKey(
        'lib_collections.CollectionPage', related_name="col_obj_metadata"
    )


class CResult(models.Model):
    """
    Class for search results within a Collection Page.
    """
    field_label = models.CharField(max_length=255, blank=True)
    field_identifier = models.CharField(
        max_length=255, blank=True, help_text="EDM/IIIF field identifier"
    )

    panels = [
        FieldPanel('field_label'),
        FieldPanel('field_identifier'),
    ]

    class Meta:
        abstract = True


class CollectionPageResult(Orderable, CResult):
    """
    Intermediate class for results within a Collection Page.
    (needed to create an InlinePanel)
    """
    page = ParentalKey(
        'lib_collections.CollectionPage', related_name="col_result"
    )


class CFacet(models.Model):
    """
    Class for facets within a Collection Page.
    """
    label = models.CharField(max_length=255, blank=True)
    search_handler_location = models.CharField(max_length=255, blank=True)
    includes_ocr = models.BooleanField(
        default=False, help_text='Do the searchable objects have OCR?'
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel('label'),
                FieldPanel('search_handler_location'),
                FieldPanel('includes_ocr'),
            ]
        ),
    ]

    class Meta:
        abstract = True


class CollectionPageFacet(Orderable, CFacet):
    """
    Intermediate class for facets within a Collection Page.
    (needed to create an InlinePanel)
    """
    page = ParentalKey(
        'lib_collections.CollectionPage', related_name="col_facet"
    )


class CBrowse(models.Model):
    """
    Class for cluster browses within a Collection Page.
    """
    label = models.CharField(max_length=255, blank=True)
    include = models.BooleanField(
        default=False,
        help_text=(
            'Include browse term in collection sidebar? \
            (Featured browse)'
        )
    )
    iiif_location = models.URLField(max_length=255, blank=True)
    link_text_override = models.CharField(max_length=255, blank=True)

    panels = [
        MultiFieldPanel(
            [
                FieldPanel('label'),
                FieldPanel('include'),
                FieldPanel('iiif_location'),
                FieldPanel('link_text_override'),
            ]
        ),
    ]

    class Meta:
        abstract = True


class CollectionPageClusterBrowse(Orderable, CBrowse):
    """
    Intermediate class for cluster browses within a Collection Page.
    (needed to create an InlinePanel)
    """
    page = ParentalKey(
        'lib_collections.CollectionPage', related_name="col_cbrowse"
    )


class LBrowse(models.Model):
    """
    Class for list browses within a Collection Page.
    """
    label = models.CharField(max_length=255, blank=True)
    include = models.BooleanField(
        default=False,
        help_text=(
            'Include browse term in collection sidebar? \
            (Featured browse)'
        )
    )
    iiif_location = models.URLField(max_length=255, blank=True)
    link_text_override = models.CharField(max_length=255, blank=True)

    panels = [
        MultiFieldPanel(
            [
                FieldPanel('label'),
                FieldPanel('include'),
                FieldPanel('iiif_location'),
                FieldPanel('link_text_override'),
            ]
        ),
    ]

    class Meta:
        abstract = True


class CollectionPageListBrowse(Orderable, LBrowse):
    """
    Intermediate class for list browses within a Collection Page.
    (needed to create an InlinePanel)
    """
    page = ParentalKey(
        'lib_collections.CollectionPage', related_name="col_lbrowse"
    )


class CSearch(models.Model):
    """
    Class for searches within a Collection Page.
    """
    label = models.CharField(max_length=255, blank=True)
    include = models.BooleanField(
        default=False, help_text='Include in sidebar?'
    )
    default = models.BooleanField(
        default=False,
        help_text=(
            'Is this the default search? (If more than one are selected, the \
            first one selected will be the default.)'
        )
    )
    mark_logic_parameter = models.CharField(max_length=255, blank=True)
    search_handler_location = models.CharField(max_length=255, blank=True)
    includes_ocr = models.BooleanField(
        default=False, help_text='Do the searchable objects have OCR?'
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel('label'),
                FieldPanel('include'),
                FieldPanel('default'),
                FieldPanel('mark_logic_parameter'),
                FieldPanel('search_handler_location'),
                FieldPanel('includes_ocr'),
            ]
        ),
    ]

    class Meta:
        abstract = True


class CollectionPageSearch(Orderable, CSearch):
    """
    Intermediate class for searches within a Collection Page.
    (needed to create an InlinePanel)
    """
    page = ParentalKey(
        'lib_collections.CollectionPage', related_name="col_search"
    )


# Collection page content type


class CollectionPage(RoutablePageMixin, PublicBasePage):
    """
    Pages for individual collections.
    """

    def __init__(self, *args, **kwargs):
        super(PublicBasePage, self).__init__(*args, **kwargs)
        self.is_viewer = False

    def metadata_field_names(self):
        """
        Convert list of metadata objects to a list of field names (strings).

        Args:
            Collection Page

        Returns:
            List of field names (strings)
        """
        metadata_fields = CollectionPageObjectMetadata.objects.filter(
            page_id=self.id
        )
        query_set = metadata_fields.values_list('edm_field_label')
        return [field[0] for field in query_set]

    def staff_context(self):
        """
        Create context dictionary containing information about the staff
        member in charge of the collection; template context then gets
        updated with this in various places.

        Args:
            Collection Page

        Returns:
            Template context dictionary
        """

        def default(thunk, defval):
            """
            Abstraction over pattern of catching an AttributeError or
            ObjectDoesNotExist exception and returning a default
            value.

            Args:
               A thunked Python expression

            Returns:
               Default input value
            """
            try:
                return thunk()
            except (AttributeError, ObjectDoesNotExist):
                return defval

        output = {}

        staff_title = default(lambda: self.staff_contact.title, '')
        staff_position_title = default(
            lambda: self.staff_contact.position_title, ''
        )
        staff_email = default(
            lambda: self.staff_contact.staff_page_email.first().email, ''
        )
        staff_phone_number = default(
            lambda: (self
                     .staff_contact
                     .staff_page_phone_faculty_exchange
                     .first())
            .phone_number, ''
        )
        staff_faculty_exchange = default(
            lambda: (self
                     .staff_contact
                     .staff_page_phone_faculty_exchange
                     .first())
            .faculty_exchange, ''
        )
        staff_url = default(
            lambda: (StaffPublicPage
                     .objects
                     .get(cnetid=self.staff_contact.cnetid)
                     .url),
            ''
        )

        access_location = default(
            lambda: {
                "url": self.collection_location.url,
                "title": self.collection_location.title
            }, ''
        )

        unit_title = lazy_dotchain(lambda: self.unit.title, '')
        unit_url = lazy_dotchain(lambda: self.unit.public_web_page.url, '')
        unit_email_label = lazy_dotchain(lambda: self.unit.email_label, '')
        unit_email = lazy_dotchain(lambda: self.unit.email, '')
        unit_phone_label = lazy_dotchain(
            lambda: self.unit.unit_page_phone_number.first().phone_label, ''
        )
        unit_phone_number = lazy_dotchain(
            lambda: self.unit.unit_page_phone_number.first().phone_number, ''
        )
        unit_fax_number = lazy_dotchain(lambda: self.unit.fax_number, '')
        unit_link_text = lazy_dotchain(lambda: self.unit.link_text, '')
        unit_link_external = lazy_dotchain(lambda: self.unit.link_external, '')
        unit_link_page = lazy_dotchain(lambda: self.unit.link_page.url, '')
        unit_link_document = lazy_dotchain(
            lambda: self.unit.link_document.file.url, ''
        )

        related_collections = lazy_dotchain(
            lambda: self.related_collection_placement.all(), ''
        )
        related_exhibits = lazy_dotchain(
            lambda: self.exhibit_page_related_collection.all(), ''
        )
        collections_by_subject = lazy_dotchain(
            lambda: self.collection_subject_placements.all(), ''
        )
        collections_by_format = lazy_dotchain(
            lambda: self.collection_placements.all(), ''
        )

        output['staff_title'] = staff_title
        output['staff_position_title'] = staff_position_title
        output['staff_email'] = staff_email
        output['staff_phone_number'] = staff_phone_number
        output['staff_faculty_exchange'] = staff_faculty_exchange
        output['staff_url'] = staff_url

        output['unit_title'] = unit_title
        output['unit_url'] = unit_url
        output['unit_email'] = unit_email
        output['unit_email_label'] = unit_email_label
        output['unit_phone_label'] = unit_phone_label
        output['unit_phone_number'] = unit_phone_number
        output['unit_fax_number'] = unit_fax_number
        output['unit_link_text'] = unit_link_text
        output['unit_link_external'] = unit_link_external
        output['unit_link_page'] = unit_link_page
        output['unit_link_document'] = unit_link_document

        output["access_location"] = access_location

        output["related_collections"] = related_collections
        output["collections_by_subject"] = collections_by_subject
        output["related_exhibits"] = related_exhibits
        output["collections_by_format"] = collections_by_format

        return output

    def build_breadcrumbs(request):
        """
        Create breadcrumb trail.

        Args:
            HTTP request

        Returns:
            Tuple containing breadcrumb trail, along with the
            final breadcrumb text (which is different because it isn't
            a link)
        """
        breadcrumbs = list(
            filter(lambda x: x != "", request.path.split('/'))
        )

        trimmed_crumbs = breadcrumbs[2:-1]
        final_crumb = breadcrumbs[-1]

        unslugify_browse = DisplayBrowse.unslugify_browse

        def path_up_to(idx, lst):
            return {
                unslugify_browse(lst[i - 1]):
                ("/collex/collections/" + "/".join(lst[:i]))
                for i in range(1, idx + 1)
                if lst[i - 1] not in [
                    'list-browse',
                    'object',
                    'cluster-browse',
                ]
            }

        breads = path_up_to(len(trimmed_crumbs), trimmed_crumbs)
        return (breads, final_crumb)

    def override(new_string, string):
        """
        Reset name of link text for list browse to be 'All Maps'

        Args:
            Link text

        Returns:
            New link text: 'All Maps'
        """
        if new_string:
            return new_string
        else:
            return string

    def build_browse_types(self):
        """
        Create dictionary containing information needed to generate
        sidebar links for all the different browse types.

        Args:
            Collection page

        Returns:
            Dictionary representing information in sidebar browse
            links
        """
        slug = self.slug

        # bring CBrowseURL utility functions into local namespace
        mk_cbrowse_type_url_wagtail = CBrowseURL.mk_cbrowse_type_url_wagtail
        mk_lbrowse_url_wagtail = LBrowseURL.mk_lbrowse_url_wagtail

        return OrderedDict(
            [(CollectionPage.override(x.link_text_override, x.label),
              mk_cbrowse_type_url_wagtail(slug, slugify(x.label)))
             for x in CollectionPageClusterBrowse
             .objects
             .filter(page=self)]
            +
            [(CollectionPage.override(x.link_text_override, x.label),
              mk_lbrowse_url_wagtail(slug, slugify(x.label)))
             for x in CollectionPageListBrowse
             .objects
             .filter(page=self)]
        )

    # Main Admin Panel Fields
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
    primary_online_access_link_label = models.CharField(
        max_length=255, blank=True
    )
    primary_online_access_link_url = models.URLField(
        "Primary online access link URL", blank=True
    )
    collection_location = models.ForeignKey(
        'public.LocationPage', null=True, blank=True, on_delete=models.SET_NULL
    )
    staff_contact = models.ForeignKey(
        'staff.StaffPage', null=True, blank=True, on_delete=models.SET_NULL
    )
    unit_contact = models.BooleanField(default=False)

    # Collection Panel Fields
    # tab in the admin interface is called 'Collection'
    digital_collection = models.BooleanField(
        default=False, help_text='Is this a Digital Collection?'
    )
    hex_regex = RegexValidator(
        regex='^#[a-zA-Z0-9]{6}$',
        message='Please enter a hex color, e.g. #012043'
    )
    branding_color = models.CharField(
        validators=[hex_regex], max_length=7, blank=True
    )
    google_font_link = models.URLField(
        blank=True, help_text='Google fonts link to embed in the header'
    )
    font_family = models.CharField(
        max_length=100,
        blank=True,
        help_text='CSS font-family value, e.g. \'Roboto\', sans-serif'
    )
    citation_config = models.TextField(
        default=CitationInfo.default_config,
        help_text=(
            'INI-style configuration for Citation service, saying which'
            ' metadata fields to pull from the Turtle data on the object; '
            'see https://github.com/uchicago-library/uchicago-library.github.io '
            'for more info on how to edit/construct one of these'
        ),
        verbose_name="Citation Configuration",
    )
    highlighted_records = models.URLField(
        blank=True,
        help_text=(
            'URL for the select objects you would \
            like to show in the collection page'
        )
    )

    # TODO: eventually this will contain instructions for generating a
    # link to the library catalog or other kinds of specialized links

    object_identifier = models.URLField(
        max_length=255,
        blank=True,
        help_text=(
            'Use a Bib ID or a record PI to construct \
            a link to the catalog'
        )
    )

    @route(r'^object/(?P<manifid>\w+)/$')
    def object(self, request, *args, **kwargs):
        """
        Route for digital collection object page.
        """
        template = "lib_collections/collection_object_page.html"

        # list of metadata fields from Mark Logic to display in object page
        field_names = self.metadata_field_names()

        # object NOID
        manifid = kwargs["manifid"]

        slug = self.slug

        # gather information for sidebar browse links
        sidebar_browse_types = self.build_browse_types()

        def injection_safe(id):
            """
            Check that URL route ends in a well-formed NOID.  This is mostly
            just a simple safeguard against possible SparQL injection
            attacks.

            Args:
                Candidate NOID

            Returns:
                Boolean

            """
            length_ok = len(id) >= 1 and len(id) <= 30
            alphanum = id.isalnum()
            return length_ok and alphanum

        # query Mark Logic for object metadata
        if injection_safe(manifid):
            marklogic = get_record_for_display(
                manifid,
                field_names,
            )
        else:
            raise Http404

        def truncate_crumb(crumb, length):
            """
            Truncate breadcrumb trail link text at a given number of
            characters.

            Args:
                Link text, Max link text length

            Returns:
                New link text
            """
            if len(crumb) >= length:
                return crumb[:length].rstrip() + ' ...'
            else:
                return crumb

        # construct breadcrumb trail
        breads, final_crumb = CollectionPage.build_breadcrumbs(request)

        # adjust value of final breadcrumb to show object title if possible
        if not marklogic:
            object_title = 'Object'
            final_crumb = object_title
        elif 'Title' in marklogic.keys():
            object_title = marklogic['Title'].split(',')[0]
            final_crumb = truncate_crumb(object_title,
                                         COLLECTION_OBJECT_TRUNCATE)
        elif 'Description' in marklogic.keys():
            object_title = marklogic['Description'].split(',')[0]
            final_crumb = truncate_crumb(object_title,
                                         COLLECTION_OBJECT_TRUNCATE)
        else:
            object_title = 'Object'
            final_crumb = object_title

        def default(thunk, defval):
            """
            Abstraction over the repeated pattern of catching a KeyError
            exception and returning a default value.

            Args:
                Dictionary lookup

            Returns:
                Value corresponding to the key (or the default in
                case of a key error)
            """
            try:
                return thunk()
            except (KeyError, TypeError):
                return defval

        def callno_to_pi(callno):
            return '-'.join(
                callno.replace(':', ' ').replace('.', ' ').upper().split()
            )

        # get link to physical object in VuFind
        physical_object = default(
            lambda: get_record_no_parsing(manifid, '')['Local'], ''
        )
        callno = default(
            lambda: get_record_no_parsing(manifid, '')['Classificationlcc'], ''
        )

        # get link to catalog call number for collection object

        def linkify(service, pi):
            """
            Build BTAA/LUNA link.

            Args:
                External Service instance, Permanent Identifier string

            Returns:
                Dictionary containing information for BTAA/LUNA
                links in object template
            """
            if service.get_service_display() == 'LUNA':
                return {
                    'service':
                    'LUNA',
                    'caption':
                    'Assemble Slide Decks',
                    'link': (
                        'https://luna.lib.uchicago.edu/'
                        'luna/servlet/view/search'
                        '?q=_luna_media_exif_filename='
                        '%s.tif'
                    ) % pi,
                }
            elif service.get_service_display() == 'BTAA':
                return {
                    'service': 'BTAA Geoportal',
                    'caption': 'Discover Maps & GIS Data',
                    'link': service.identifier,
                }
            else:
                return {}

        # build BTAA/LUNA links
        external_links = [
            linkify(service, callno_to_pi(callno))
            for service in self.col_external_service.all()
        ]

        # bring utility functions from DisplayBrowse into local namespace
        get_viewer_url = IIIFDisplay.get_viewer_url
        unslugify_browse = DisplayBrowse.unslugify_browse

        # bring utility functions from CitationInfo into local namespace

        # MT 3/23/2021: commented out temporarily while we overhaul
        # the citation service

        # get_turtle_data = CitationInfo.get_turtle_data
        # get_csl = CitationInfo.get_csl
        # get_bibtex = CitationInfo.get_bibtex
        # get_ris = CitationInfo.get_ris
        # get_zotero = CitationInfo.get_zotero
        # csl_json_to_html = CitationInfo.csl_json_to_html
        # config = self.citation_config

        # get Turtle data for collection object
        # turtle_data = get_turtle_data(manifid)

        # get CSL-JSON data
        # csl = get_csl(
        #     turtle_data,
        #     config,
        # )

        # get CSL files for Chicago, MLA, and APA styles off disk

        # chicago = csl_json_to_html(csl, CHICAGO_PATH)
        # mla = csl_json_to_html(csl, MLA_PATH)
        # apa = csl_json_to_html(csl, APA_PATH)

        # get Bibtex, RIS, and Zotero harvesting citation info
        # bibtex_link = get_bibtex(turtle_data, config)
        # endnote_link = get_ris(turtle_data, config)
        # zotero = str(get_zotero(turtle_data, config))

        # URLs for social media sharing links
        share_url = request.build_absolute_uri()
        og_url = "http://www.lib.uchicago.edu/ark:/61001/" + manifid
        canonical_url = og_url

        iiif_url = get_viewer_url(manifid)

        internal_error = not marklogic and not iiif_url

        # populate context

        # MT: citation-related stuff temprarily commented out: see
        # above note

        context = super().get_context(request)
        context["manifid"] = manifid
        context["iiif_url"] = iiif_url
        context["share_url"] = share_url
        context["slug"] = slug
        context["internal_error"] = internal_error
        context["marklogic"] = marklogic
        context["sidebar_browse_types"] = sidebar_browse_types
        context["external_links"] = external_links
        context['collection_final_breadcrumb'] = unslugify_browse(final_crumb)
        context['collection_breadcrumb'] = breads
        context['object_title'] = object_title
        context['physical_object'] = physical_object
        context['callno'] = callno

        # context['chicago'] = chicago
        # context['mla'] = mla
        # context['apa'] = apa
        # context['bibtex_link'] = bibtex_link
        # context['endnote_link'] = endnote_link
        # context['zotero'] = zotero

        context['og_url'] = og_url
        context['canonical_url'] = canonical_url

        # update context with staff info for sidebar
        context.update(self.staff_context())

        # at long last, we are done defining this route
        return TemplateResponse(request, template, context)

    @route(r'^cluster-browse/(?P<browse_type>[-\w]+/){0,1}$')
    def cluster_browse_list(self, request, *args, **kwargs):
        """
        Route for listing of multiple cluster browses.  For example: the
        list of all Subject browses.
        """

        template = "lib_collections/collection_browse.html"

        slug = self.slug

        # bring DisplayBrowse functions into local namespace
        get_iiif_labels = DisplayBrowse.get_iiif_labels
        unslugify_browse = DisplayBrowse.unslugify_browse

        # construct browse type links for sidebar
        sidebar_browse_types = self.build_browse_types()

        all_browse_types = (
            CollectionPageClusterBrowse
            .objects
            .filter(page=self)
        )

        try:
            browse_type = kwargs["browse_type"]
        except KeyError:
            browse_type = ''

        if not browse_type:
            # default to subject browses if no browse type is specified in
            # route
            default_browse = all_browse_types.first()
            default = default_browse.label.lower()
            browse_type = default
            browse_title = unslugify_browse(browse_type)
        else:
            # otherwise, get the browse type from the route
            browse_type = kwargs["browse_type"][:-1]
            browse_title = unslugify_browse(browse_type)

        # construct breadcrumb trail
        breads, final_crumb = CollectionPage.build_breadcrumbs(request)

        # bring CBrowseURL function into local namespace
        mk_cbrowse_type_url_iiif = CBrowseURL.mk_cbrowse_type_url_iiif

        names = [x.label.lower() for x in all_browse_types]

        try:
            browses = get_iiif_labels(
                mk_cbrowse_type_url_iiif(slug, browse_type),
                browse_type,
                slug,
            )
            internal_error = False
        except (KeyError, simplejson.JSONDecodeError):
            browses = ''
            internal_error = True

        browse_is_ready = browse_type in names and browses

        # populate context
        context = super().get_context(request)
        context["sidebar_browse_types"] = sidebar_browse_types
        context["browses"] = browses
        context["browse_title"] = browse_title
        context["browse_is_ready"] = browse_is_ready
        context["internal_error"] = internal_error
        context['collection_final_breadcrumb'] = unslugify_browse(final_crumb)
        context['collection_breadcrumb'] = breads

        return TemplateResponse(request, template, context)

    @ route(r'^cluster-browse/(?P<browse_type>[-\w]+)/(?P<browse>[-\w]+)/$')
    def cluster_browse(self, request, *args, **kwargs):
        """
        Route for listing a particular cluster browse.  For example: the
        list of objects falling under the Criminals Subject browse.
        """

        template = "lib_collections/collection_browse.html"

        slug = self.slug

        # pull browse information from URL
        browse_s = kwargs['browse']
        browse_type_s = kwargs['browse_type']

        all_browse_types = (
            CollectionPageClusterBrowse
            .objects
            .filter(page=self)
        )

        names = [x.label.lower() for x in all_browse_types]

        # construct browse type dictionary for sidebar
        sidebar_browse_types = self.build_browse_types()

        try:
            objects = DisplayBrowse.get_cbrowse_items(
                slug,
                browse_s,
                browse_type_s,
            )
            internal_error = False
        except (KeyError,
                simplejson.JSONDecodeError):
            objects = ''
            internal_error = True

        # construct breadcrumb trail
        breads, final_crumb = CollectionPage.build_breadcrumbs(request)

        # get DisplayBrowse helper function into local namespace
        unslugify_browse = DisplayBrowse.unslugify_browse

        browse_is_ready = browse_type_s in names and objects

        # convert browse and browse type slugs into something suitable for
        # display
        browse = unslugify_browse(browse_s)
        browse_type = unslugify_browse(browse_type_s)

        # construct context
        context = super().get_context(request)
        context["browse_title"] = browse
        context["browse_type"] = browse_type
        context["sidebar_browse_types"] = sidebar_browse_types
        context["slug"] = slug
        context["objects"] = objects
        context["internal_error"] = internal_error
        context["browse_is_ready"] = browse_is_ready
        context['collection_final_breadcrumb'] = unslugify_browse(final_crumb)
        context['collection_breadcrumb'] = breads

        return TemplateResponse(request, template, context)

    @ route(r'^list-browse/(?P<browse_name>[-\w]+/)(?P<pageno>[0-9]*/){0,1}$')
    def list_browse(self, request, *args, **kwargs):
        """
        Route for main list browse index.
        """

        # display a max of 25 items per page
        THUMBS_PER_PAGE = 25

        template = "lib_collections/collection_browse.html"

        collection = self.slug

        paginate_name = kwargs['browse_name']

        browse_name = paginate_name[:-1]

        all_browse_types = (
            CollectionPageListBrowse
            .objects
            .filter(page=self)
        )

        names = [x.label.lower() for x in all_browse_types]

        try:
            pageno = int(kwargs["pageno"][:-1])
        except KeyError:
            pageno = 1

        # list of browse types for sidebar
        sidebar_browse_types = self.build_browse_types()

        # retrieve list browse information from IIIF server

        try:
            objects = DisplayBrowse.get_lbrowse_items(
                collection,
                browse_name,
            )
            internal_error = False
        except (KeyError,
                simplejson.JSONDecodeError):
            objects = ''
            internal_error = True

        # create pagination
        list_objects = Paginator(objects, THUMBS_PER_PAGE)

        # construct breadcrumb trail
        breads, final_crumb = CollectionPage.build_breadcrumbs(request)

        unslugify_browse = DisplayBrowse.unslugify_browse

        current_browse = CollectionPageListBrowse.objects.filter(
            label=unslugify_browse(browse_name), page=self).first()

        if current_browse:
            browse_title = CollectionPage.override(
                current_browse.link_text_override,
                "Browse by %s" % current_browse.label)
            collection_final_breadcrumb = CollectionPage.override(
                current_browse.link_text_override,
                unslugify_browse(final_crumb)
            )
        else:
            browse_title = unslugify_browse(browse_name)
            collection_final_breadcrumb = unslugify_browse(final_crumb)

        # final breadcrumb just says e.g. Page 2
        try:
            int(final_crumb)
            final_crumb = ('Page ' + final_crumb)
        except ValueError:
            pass

        browse_is_ready = browse_name in names and objects

        # return HttpResponse(browse_name)

        # populate context
        context = super().get_context(request)
        context["browse_title"] = browse_title
        context["sidebar_browse_types"] = sidebar_browse_types
        context["browse_is_ready"] = browse_is_ready
        context["internal_error"] = internal_error
        context["list_objects"] = list_objects.page(pageno)
        context["root_link"] = "/collex/collections/%s/list-browse/%s" % (
            collection, paginate_name
        )
        context['collection_final_breadcrumb'] = collection_final_breadcrumb
        context['collection_breadcrumb'] = breads

        return TemplateResponse(request, template, context)

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
        InlinePanel(
            'supplementary_access_links', label='Supplementary Access Links'
        ),
        InlinePanel('related_collection_placement',
                    label='Related Collection'),
        FieldPanel('collection_location'),
        InlinePanel('donor_page_list_placement', label='Donor'),
        MultiFieldPanel(
            [FieldPanel('staff_contact'),
             FieldPanel('unit_contact')],
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

    # panels within the 'Collection' tab in the admin interface
    collection_panels = [
        # FieldPanel('digital_collection'),
        # MultiFieldPanel(
        #     [
        #         ImageChooserPanel('banner_image'),
        #         ImageChooserPanel('banner_feature'),
        #         FieldPanel('banner_title'),
        #         FieldPanel('banner_subtitle'),
        #     ],
        #     heading='Banner'
        # ),
        # MultiFieldPanel(
        #     [
        #         FieldPanel('branding_color'),
        #         FieldPanel('google_font_link'),
        #         FieldPanel('font_family'),
        #     ],
        #     heading='Branding'
        # ),
        FieldPanel('highlighted_records'),
        FieldPanel('citation_config'),
        InlinePanel('col_search', label='Searches'),
        InlinePanel('col_lbrowse', label='List Browses'),
        InlinePanel('col_cbrowse', label='Cluster Browses'),
        InlinePanel('col_facet', label='Facets'),
        InlinePanel('col_result', label='Additional Fields in Results'),
        InlinePanel('col_obj_metadata', label='Object Metadata'),
        InlinePanel('col_external_service', label='Link to External Service'),
    ]

    # this creates the 'Collection' tab in the admin interface
    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading='Content'),
            ObjectList(PublicBasePage.promote_panels, heading='Promote'),
            ObjectList(
                Page.settings_panels, heading='Settings', classname="settings"
            ),
            ObjectList(collection_panels, heading='Collection'),
        ]
    )

    def get_context(self, request):

        # get URL for highlighted records listing from Wagtail database
        iiif_url = self.highlighted_records

        # display first five records in selected listing
        if iiif_url:
            r = requests.get(iiif_url)
            j = r.json()
            objects = [
                DisplayBrowse.prepare_browse_json(x, DisplayBrowse.comma_join)
                for x in j['items']
            ][:5]
        else:
            objects = []

        # browse links for sidebar
        sidebar_browse_types = self.build_browse_types()

        default_image = None
        default_image = Image.objects.get(title="Default Placeholder Photo")

        # populate context
        context = super(CollectionPage, self).get_context(request)
        context['default_image'] = default_image
        context['sidebar_browse_types'] = sidebar_browse_types
        context['objects'] = objects

        # update context with information about staff associated with the
        # relevant collection
        context.update(self.staff_context())

        return context

    def has_right_sidebar(self):
        return True


# CollectingArea page models


class RegionalCollection(models.Model):
    """
    Abstract model for regional collections.
    """
    regional_collection_name = models.CharField(max_length=254, blank=True)
    regional_collection_url = models.URLField(
        "Regional Collection URL", blank=True, null=True
    )
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
    page = ParentalKey(
        'lib_collections.CollectingAreaPage',
        related_name='regional_collections'
    )


class RelatedCollectingAreas(Orderable, models.Model):
    """
    Through table for repeatable regional collections.
    """
    parent = ParentalKey(
        'lib_collections.CollectingAreaPage',
        related_name='related_collecting_areas',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    related_collecting_area = models.ForeignKey(
        'CollectingAreaPage',
        related_name='related_collecting_area',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )


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
    page = ParentalKey(
        'lib_collections.CollectingAreaPage', related_name='lib_guides'
    )


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
    collecting_statement = StreamField(
        DefaultBodyFields(), blank=False, null=True
    )
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
    collection_location = models.ForeignKey(
        'public.LocationPage', null=True, blank=True, on_delete=models.SET_NULL
    )
    reference_materials = RichTextField(blank=True, null=True)
    circulating_materials = RichTextField(blank=True, null=True)
    archival_link_text = models.CharField(
        max_length=255, blank=True, null=True)
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
    supplementary_header = models.CharField(
        max_length=255, blank=True, null=True
    )
    supplementary_text = RichTextField(blank=True, null=True)

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
        MultiFieldPanel(
            [
                PageChooserPanel(
                    'first_feature', [
                        'lib_collections.CollectionPage',
                        'lib_collections.ExhibitPage'
                    ]
                ),
                PageChooserPanel(
                    'second_feature', [
                        'lib_collections.CollectionPage',
                        'lib_collections.ExhibitPage'
                    ]
                ),
                PageChooserPanel(
                    'third_feature', [
                        'lib_collections.CollectionPage',
                        'lib_collections.ExhibitPage'
                    ]
                ),
                PageChooserPanel(
                    'fourth_feature', [
                        'lib_collections.CollectionPage',
                        'lib_collections.ExhibitPage'
                    ]
                ),
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
        InlinePanel(
            'related_collecting_areas', label='Related Collecting Area'
        ),
        InlinePanel(
            'regional_collections',
            label='Other Local Collections',
            help_text=(
                'Related collections that are held by other \
                institutions, like BMRC, Newberry, etc.'
            ),
        )
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
            A set of subjects or an empty set
        """
        if self.subject is None:
            return set([])
        elif children:
            return set(self.subject.get_descendants())
        else:
            return set([self.subject])

    def _build_related_link(self, page_id, site):
        """
        Args:
            page_id, integer

            site: object

        Return:
            tuple of strings representing a link to
            a page where the first item in the tuple
            is a page title and the second item is a url.
        """
        try:
            page = Page.objects.get(id=page_id)
            title = str(page)
            url = page.relative_url(site)
        except (Page.DoesNotExist):
            return ('', '')
        return (title, url)

    def _build_subject_specialist(self, librarian, site):
        """
        Build a data object representing a subject
        specialist.

        Args:
            librarian: StaffPage object.

            site: object

        Returns:
            Mixed tuple
        """
        is_staff_page = librarian.__class__.__name__ == 'StaffPage'
        if not is_staff_page:
            raise TypeError('The wrong page type was passed')
        staff_member = str(librarian)
        title = librarian.position_title
        url = librarian.public_page.relative_url(site)
        thumb = librarian.profile_picture
        try:
            email = librarian.staff_page_email.values_list('email',
                                                           flat=True)[0]
        except:
            email = ''
        phone_and_fac = tuple(
            librarian.staff_page_phone_faculty_exchange.values_list(
                'phone_number', 'faculty_exchange'
            )
        )
        return (staff_member, title, url, email, phone_and_fac, thumb)

    def get_related(self, site, children=False):
        """
        Get related exhibits or collections by subject.

        Args:
            children: boolean, show hierarchical subjects.

            site: object

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
        related = {'collections': set([]), 'exhibits': set([])}
        subjects = self.get_subjects(children)
        # Related collections and exhibits
        for subject in subjects:
            related['collections'] = related['collections'] | set(
                self._build_related_link(page[0], site)
                for page in subject.collection_pages.values_list('page_id')
            )
            related['exhibits'] = related['exhibits'] | set(
                self._build_related_link(page[0], site)
                for page in subject.exhibit_pages.values_list('page_id')
            )

        # Staff pages for subject specialists
        # Can make this more efficient if HR starts using the employee_type field
        librarians = StaffPage.objects.live()
        subject_specialists = set([])
        for staff in librarians:
            intersecting = len(
                staff.get_subject_objects().intersection(subjects)
            ) > 0
            if intersecting:
                subject_specialists.add(
                    self._build_subject_specialist(staff, site)
                )
        related['subject_specialists'] = subject_specialists
        return related

    def get_features(self, site):
        """
        Return a list of tuples representing featured CollectionPages
        or ExhibitPages.

        Args:
            site: object

        Return:
            A list of tuples representing featured collections
            and exhibits. Each tupal has four items: 1. string
            representing the page title, 2. string, page url,
            3. string, short description, 4. image object.
        """
        retval = []
        features = [
            self.first_feature, self.second_feature, self.third_feature,
            self.fourth_feature
        ]
        for feature in features:
            if feature:
                retval.append(
                    (
                        str(feature), feature.relative_url(site),
                        feature.specific.short_abstract,
                        feature.specific.thumbnail
                    )
                )
        return retval

    def get_context(self, request):
        """
        Override the page object's get context method.
        """
        context = super(CollectingAreaPage, self).get_context(request)

        current_site = Site.find_for_request(request)
        related = self.get_related(current_site, False)
        limit = -1
        context['related_collections'] = sorted(related['collections'])[:limit]
        context['related_exhibits'] = sorted(related['exhibits'])[:limit]
        context['related_subject_specialists'] = sorted(
            related['subject_specialists']
        )
        context['features'] = self.get_features(current_site)
        context['lib_guides'] = self.lib_guides.get_object_list()

        try:
            regional_collections = self.regional_collections.all()
        except (AttributeError):
            regional_collections = []
        context['regional_collections'] = regional_collections
        return context


class ExhibitPageSubjectPlacement(Orderable, models.Model):
    page = ParentalKey(
        'lib_collections.ExhibitPage',
        on_delete=models.CASCADE,
        related_name='exhibit_subject_placements'
    )
    subject = models.ForeignKey(
        'subjects.Subject',
        on_delete=models.CASCADE,
        related_name='exhibit_pages'
    )

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
    staff_contact = models.ForeignKey(
        'staff.StaffPage', null=True, blank=True, on_delete=models.SET_NULL
    )
    unit_contact = models.BooleanField(default=False)
    student_exhibit = models.BooleanField(default=False)

    exhibit_open_date = models.DateField(blank=True, null=True)
    exhibit_close_date = models.DateField(blank=True, null=True)
    exhibit_location = models.ForeignKey(
        'public.LocationPage', null=True, blank=True, on_delete=models.SET_NULL
    )
    exhibit_daily_hours = models.CharField(
        blank=True, null=False, default='', max_length=255
    )
    exhibit_cost = models.CharField(
        blank=True, null=False, default='', max_length=255
    )
    space_type = models.CharField(
        null=False,
        blank=True,
        choices=(('Case', 'Case'), ('Gallery', 'Gallery')),
        max_length=255
    )
    web_exhibit_url = models.URLField("Web Exhibit URL", blank=True)
    publication_description = models.CharField(
        null=False, blank=True, default='', max_length=255
    )
    publication_price = models.CharField(
        null=False, blank=True, default='', max_length=255
    )
    publication_url = models.URLField("Publication URL", blank=True)
    ordering_information = models.BooleanField(default=False)

    exhibit_text_link_external = models.URLField(
        "Exhibit text external link", blank=True
    )
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

    exhibit_checklist_link_external = models.URLField(
        "Exhibit checklist external link", blank=True
    )
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
    web_exhibit = models.BooleanField(
        default=False, help_text='Display as web exhibit'
    )
    hex_regex = RegexValidator(
        regex='^#[a-zA-Z0-9]{6}$',
        message='Please enter a hex color, e.g. #012043'
    )
    branding_color = models.CharField(
        validators=[hex_regex], max_length=7, blank=True
    )
    google_font_link = models.URLField(
        blank=True, help_text='Google fonts link to embedd in the header'
    )
    font_family = models.CharField(
        max_length=100,
        blank=True,
        help_text='CSS font-family value, e.g. \'Roboto\', sans-serif'
    )

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
            [ImageChooserPanel('thumbnail'),
             FieldPanel('thumbnail_caption')],
            heading='Thumbnail'
        ),
        InlinePanel('exhibit_subject_placements', label='Subjects'),
        InlinePanel(
            'exhibit_page_related_collection_placement',
            label='Related Collection'
        ),
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
            [FieldPanel('staff_contact'),
             FieldPanel('unit_contact')],
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

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading='Content'),
            ObjectList(PublicBasePage.promote_panels, heading='Promote'),
            ObjectList(
                Page.settings_panels, heading='Settings', classname="settings"
            ),
            ObjectList(web_exhibit_panels, heading='Web Exhibit'),
        ]
    )

    @property
    def is_current_exhibit(self):
        """
        Determines if the exhibit is current.

        Returns:
            Boolean
        """
        today = datetime.datetime.now().date()
        open_date = self.exhibit_open_date
        close_date = self.exhibit_close_date
        if open_date and close_date:
            is_open = open_date.__lt__(today)
            not_closed = close_date.__gt__(today)
            return is_open and not_closed
        return False

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
        # building = self.location_and_hours['page_location'].id
        img = {
            SCRC_BUILDING_ID: SCRC_EXHIBIT_FOOTER_IMG,
            CRERAR_BUILDING_ID: CRERAR_EXHIBIT_FOOTER_IMG
        }
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
                    related_collections += '<li><a href="' + collection.related_collection.relative_url(
                        current_site
                    ) + '">' + collection.related_collection.title + '</a></li>'
            return related_collections + '</ul>'
        return None

    def get_context(self, request):
        staff_url = ''
        try:
            staff_url = StaffPublicPage.objects.get(
                cnetid=self.staff_contact.cnetid
            ).url
        except:
            pass
        default_image = None
        default_image = Image.objects.get(title="Default Placeholder Photo")

        font = DEFAULT_WEB_EXHIBIT_FONT
        if self.font_family:
            font = self.font_family

        unit_title = lazy_dotchain(lambda: self.unit.title, '')
        unit_url = lazy_dotchain(lambda: self.unit.public_web_page.url, '')
        unit_email_label = lazy_dotchain(lambda: self.unit.email_label, '')
        unit_email = lazy_dotchain(lambda: self.unit.email, '')
        unit_phone_label = lazy_dotchain(
            lambda: self.unit.unit_page_phone_number.first().phone_label, ''
        )
        unit_phone_number = lazy_dotchain(
            lambda: self.unit.unit_page_phone_number.first().phone_number, ''
        )
        unit_fax_number = lazy_dotchain(lambda: self.unit.fax_number, '')
        unit_link_text = lazy_dotchain(lambda: self.unit.link_text, '')
        unit_link_external = lazy_dotchain(lambda: self.unit.link_external, '')
        unit_link_page = lazy_dotchain(lambda: self.unit.link_page.url, '')
        unit_link_document = lazy_dotchain(
            lambda: self.unit.link_document.file.url, ''
        )

        context = super(ExhibitPage, self).get_context(request)
        footer_img = self.get_web_exhibit_footer_img(
            self.location_and_hours['page_location'].id
        )  # must be set after context
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
        context['unit_contact'] = self.unit_contact
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
        footer_img = exhibit.get_web_exhibit_footer_img(
            self.location_and_hours['page_location'].id
        )

        font = DEFAULT_WEB_EXHIBIT_FONT
        if exhibit.font_family:
            font = exhibit.font_family

        context['branding_color'] = exhibit.branding_color
        context['font_family'] = font
        context['google_font_link'] = exhibit.google_font_link
        context['footer_img'] = footer_img
        context['has_exhibit_footer'] = not (not footer_img)
        context['is_web_exhibit'] = True
        context['related_collections'] = exhibit.get_related_collections(
            request
        )
        context['exhibit_open_date'] = exhibit.exhibit_open_date
        context['exhibit_close_date'] = exhibit.exhibit_close_date
        context['exhibit_close_date'] = exhibit.exhibit_location
        return context
