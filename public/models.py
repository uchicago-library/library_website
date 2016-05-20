from django.db import models
from django import forms
from django.utils import timezone
from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailcore import blocks
from wagtail.wagtailadmin.edit_handlers import TabbedInterface, ObjectList, FieldPanel, FieldRowPanel, MultiFieldPanel, StreamFieldPanel, InlinePanel, PageChooserPanel
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsearch import index
from modelcluster.fields import ParentalKey
from base.models import PublicBasePage, DefaultBodyFields, Address, Email, PhoneNumber, SocialMediaFields, LinkBlock

# TEMPORARY: Fix issue # 2267:https://github.com/torchbox/wagtail/issues/2267
from wagtail.wagtailadmin.forms import WagtailAdminPageForm
from wagtail.wagtailadmin.edit_handlers import TabbedInterface as OriginalTabbedInterface
class TabbedInterface(OriginalTabbedInterface):

    def __init__(self, children, base_form_class=WagtailAdminPageForm):
        super().__init__(children, base_form_class)


class FeaturedLibraryExpertBaseBlock(blocks.StructBlock):
    """
    Base treamfield block for "Featured Library Experts".
    """
    library_expert = blocks.PageChooserBlock( # In the future Wagtail plans to allow the limiting of PageChooserBlock by page type. This will improve when we have that.
        required=False, 
    ) 
    libguides = blocks.ListBlock(LinkBlock(),
        icon='link') 


class FeaturedLibraryExpertBlock(FeaturedLibraryExpertBaseBlock):
    """
    Streamfield block for "Featured Library Experts".
    """
    start_date = blocks.DateBlock(blank=True, null=True)
    end_date = blocks.DateBlock(blank=True, null=True)

class FeaturedLibraryExpertBaseFields(blocks.StreamBlock):
    """
    Base fields for a Featured Library Expert.
    """
    person = FeaturedLibraryExpertBaseBlock(
        icon='view', 
        required=False, 
        template='public/blocks/featured_library_expert.html'
    )


class FeaturedLibraryExpertFields(blocks.StreamBlock):
    """
    All fields for a Featured Library Expert.
    """
    person = FeaturedLibraryExpertBlock(
        icon='view', 
        required=False, 
        template='public/blocks/featured_library_expert.html'
    )


class StandardPage(PublicBasePage, SocialMediaFields):
    """
    A standard basic page.
    """
    # Page content
    body = StreamField(DefaultBodyFields())

    # Quicklinks fields
    quicklinks = RichTextField(blank=True) 
    quicklinks_title = models.CharField(max_length=100, blank=True)
    view_more_link = models.URLField(max_length=255, blank=True, default='')
    view_more_link_label = models.CharField(max_length=100, blank=True)

    # Find spaces fields
    enable_find_spaces = models.BooleanField(default=False)
    book_a_room_link = models.URLField(max_length=255, blank=True, default='')

    # Featured collections
    collection_page = models.ForeignKey(
        'lib_collections.CollectionPage',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL
    )
 
    # Featured Library Expert
    featured_library_expert_fallback = StreamField(FeaturedLibraryExpertBaseFields(), default=[]) 
    featured_library_experts = StreamField(FeaturedLibraryExpertFields(), default=[])

    subpage_types = ['public.StandardPage', 'public.LocationPage', 'public.DonorPage', \
        'lib_collections.CollectingAreaPage', 'lib_collections.CollectionPage', 'lib_collections.ExhibitPage', \
        'redirects.RedirectPage', 'units.UnitPage', 'ask_a_librarian.AskPage', 'units.UnitIndexPage', \
        'conferences.ConferenceIndexPage', 'base.IntranetPlainPage', 'dirbrowse.DirBrowsePage', \
        'findingaids.FindingAidsPage']

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
    ] + PublicBasePage.content_panels

    widget_content_panels = [
        MultiFieldPanel(
            [
                FieldPanel('quicklinks_title'),
                FieldPanel('quicklinks'),
                FieldPanel('view_more_link_label'),
                FieldPanel('view_more_link'),
            ], 
            heading='Quicklinks'
        ),
        MultiFieldPanel(
            [
                FieldPanel('enable_find_spaces'),
                FieldPanel('book_a_room_link'),
            ], 
            heading='Find Spaces'
        ),
        MultiFieldPanel(
            [
                PageChooserPanel('collection_page', 'lib_collections.CollectionPage'),
            ], 
            heading='Featured Collection'
        ),
        StreamFieldPanel('featured_library_expert_fallback'),
        StreamFieldPanel('featured_library_experts'),
    ] + SocialMediaFields.panels

    search_fields = PublicBasePage.search_fields + (
        index.SearchField('body', partial_match=True),
    )

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(PublicBasePage.promote_panels, heading='Promote'),
        ObjectList(Page.settings_panels, heading='Settings', classname="settings"),
        ObjectList(widget_content_panels, heading='Widgets'),
    ])

    def has_field(self, field_list):
        """
        Helper method for checking the page object 
        to see if specific fields are filled out.
        Returns True if any one field is present
        in the list. Note: actually checks
        values in practice.

        Args:
            field_list: list of page field objects. 

        Returns:
            Boolean
        """
        for field in field_list:
            if field:
                return True
        return False


    def has_all_fields(self, field_list):
        """
        Helper method for checking that *all* fields
        in a given list exist. Note: actually checks
        values in practice.

        Args:
            field_list: list of page field objects. 

        Returns:
            Boolean
        """
        for field in field_list:
            if not field:
                return False
        return True


    def streamblock_has_link(self, streamblock, field):
        """
        Check that a streamfield block object has a 
        either an internal or external link when
        base.models.LinkBlock is in use.

        Args:
            streamblock: streamfield block object, 
            wagtail.wagtailcore.blocks.stream_block.StreamValue.StreamChild.

            field: string field name that contains 
            a ListBlock of LinkBlocks.
        """
        #p.featured_library_expert_fallback[0].value.get('libguides')[0].get('link_external')
        block_list = self.streamblock.value.get(field)
        for block in block_list:
            val1 = block.get('link_external')
            val2 = block.get('link_page')
            if not val1 and not val2:
                return False
        return True


    def streamblock_has_all_fields(self, streamblock, field_list):
        """
        Test to see if a streamfield block has a value for all 
        fields in a given list.

        Args:
            streamblock: streamfield block object, 
            wagtail.wagtailcore.blocks.stream_block.StreamValue.StreamChild.

            field_names: list of strings, field names.

        Returns:
            Boolean
        """
        for field in field_list:
            value = streamblock.value.get(field)
            if not value:
                return False
        return True

    @property
    def has_featured_lib_expert_fallback(self):
        """
        Test to see if a page has a "Featured 
        Library Expert" fallback set.

        Returns:
            Boolean
        """
        self.streamblock_has_all_fields(
            self.featured_library_expert_fallback[0], 
            ['library_expert']
        )


    @property 
    def has_find_spaces(self):
        """
        Determine if there is a "Find Spaces"
        widget on the page.

        Returns:
            Boolean
        """
        return self.has_field([self.enable_find_spaces])


    @property
    def has_right_sidebar(self):
        """
        Determine if a right sidebar should
        be displayed in the template.

        Returns:
            boolean
        """
        fields = [self.quicklinks, self.collection_page]
        if self.has_social_media:
            return True
        elif self.has_find_spaces:
            return True
        else:
            return self.has_field(fields)


class LocationPageDonorPlacement(Orderable, models.Model):
    """
    Create a through table for linking donor pages to location pages.
    """
    parent = ParentalKey(
        'public.LocationPage',
        related_name='location_donor_page_placements',
        null=True,
        blank=False,
        on_delete=models.SET_NULL
    )

    donor = models.ForeignKey(
        'public.DonorPage',
        related_name='location_donor_page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )


class LocationPageFloorPlacement(Orderable, models.Model):
    """
    Create a through table for linking location pages to floors.
    """
    parent = ParentalKey(
        'public.LocationPage',
        related_name='location_floor_placements',
        null=True,
        blank=False,
        on_delete=models.SET_NULL
    )

    floor = models.ForeignKey(
        'public.FloorPlanPage',
        related_name='location_floor',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )


class LocationPage(PublicBasePage, Email, Address, PhoneNumber):
    """
    Location and building pages.
    """
    # Model fields
    short_description = models.TextField(null=False, blank=False)
    long_description = RichTextField(null=False, blank=False) 
    parent_building = models.ForeignKey('self',
        null=True, blank=True, on_delete=models.SET_NULL, limit_choices_to={'is_building': True})
    location_photo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    libcal_library_id = models.IntegerField(blank=True, null=True)
    google_map_link = models.URLField(max_length=200, blank=True, default='')
    reservation_url = models.URLField(max_length=200, blank=True, default='')
    reservation_display_text = models.CharField(max_length=45, blank=True)

    # Boolean fields
    is_building = models.BooleanField(default=False)
    is_phone_zone = models.BooleanField(default=False)
    is_collaboration_zone = models.BooleanField(default=False)
    is_meal_zone = models.BooleanField(default=False)
    is_quiet_zone = models.BooleanField(default=False)
    is_study_space = models.BooleanField(default=False)
    is_teaching_space = models.BooleanField(default=False)
    is_event_space = models.BooleanField(default=False)
    is_open_space = models.BooleanField(default=False)
    is_24_hours = models.BooleanField(default=False)
    is_reservable = models.BooleanField(default=False)
    has_carrels = models.BooleanField(default=False)
    has_board = models.BooleanField(default=False)
    has_printing = models.BooleanField(default=False)
    has_soft_seating = models.BooleanField(default=False)
    has_dual_monitors = models.BooleanField(default=False)
    has_single_tables = models.BooleanField(default=False)
    has_large_tables = models.BooleanField(default=False)
    has_screen = models.BooleanField(default=False)
    has_natural_light = models.BooleanField(default=False)
    is_no_food_allowed = models.BooleanField(default=False)
    has_book_scanner = models.BooleanField(default=False)
    has_public_computer = models.BooleanField(default=False)
    is_snacks_allowed = models.BooleanField(default=False)
    has_standing_desk = models.BooleanField(default=False)
    has_lockers = models.BooleanField(default=False)
    has_day_lockers = models.BooleanField(default=False)

    ROW_CLASS = 'col4'

    # Set what appears in the admin
    content_panels = Page.content_panels + [
        FieldPanel('short_description'),
        FieldPanel('long_description'),
        FieldPanel('parent_building'),
        InlinePanel('location_floor_placements', label='Floor'),
        FieldPanel('libcal_library_id'),
        FieldPanel('google_map_link'),
        MultiFieldPanel(
            [
                FieldPanel('reservation_url'),
                FieldPanel('reservation_display_text'),
            ], 
            heading='Room Reservation Link'
        ),
        ImageChooserPanel('location_photo'),
        FieldRowPanel([
            FieldPanel('is_building', classname=ROW_CLASS),
            FieldPanel('is_phone_zone', classname=ROW_CLASS),
            FieldPanel('is_collaboration_zone', classname=ROW_CLASS),
            FieldPanel('is_meal_zone', classname=ROW_CLASS),
            FieldPanel('is_quiet_zone', classname=ROW_CLASS),
            FieldPanel('is_study_space', classname=ROW_CLASS),
            FieldPanel('is_teaching_space', classname=ROW_CLASS),
            FieldPanel('is_event_space', classname=ROW_CLASS),
            FieldPanel('is_open_space', classname=ROW_CLASS),
            FieldPanel('is_24_hours', classname=ROW_CLASS),
            FieldPanel('is_reservable', classname=ROW_CLASS),
            FieldPanel('has_carrels', classname=ROW_CLASS),
            FieldPanel('has_board', classname=ROW_CLASS),
            FieldPanel('has_printing', classname=ROW_CLASS),
            FieldPanel('has_soft_seating', classname=ROW_CLASS),
            FieldPanel('has_dual_monitors', classname=ROW_CLASS),
            FieldPanel('has_single_tables', classname=ROW_CLASS),
            FieldPanel('has_large_tables', classname=ROW_CLASS),
            FieldPanel('has_screen', classname=ROW_CLASS),
            FieldPanel('has_natural_light', classname=ROW_CLASS),
            FieldPanel('is_no_food_allowed', classname=ROW_CLASS),
            FieldPanel('has_book_scanner', classname=ROW_CLASS),
            FieldPanel('has_public_computer', classname=ROW_CLASS),
            FieldPanel('is_snacks_allowed', classname=ROW_CLASS),
            FieldPanel('has_standing_desk', classname=ROW_CLASS),
            FieldPanel('has_lockers', classname=ROW_CLASS),
            FieldPanel('has_day_lockers', classname=ROW_CLASS),
        ]),
        MultiFieldPanel(PhoneNumber.content_panels, heading='Phone Number'),
        InlinePanel('location_donor_page_placements', label='Donor'),
    ] + Email.content_panels + Address.content_panels + PublicBasePage.content_panels

    subpage_types = ['public.StandardPage', 'public.FloorPlanPage']

    search_fields = PublicBasePage.search_fields + (
        index.SearchField('short_description', partial_match=True),
        index.SearchField('long_description', partial_match=True),
        index.SearchField('parent_building'),
        index.SearchField('location_photo'),
        index.SearchField('reservation_display_url'),
        index.SearchField('reservation_display_text'),
    )


class DonorPage(PublicBasePage):
    """
    Donor page model.
    """
    description = models.TextField(null=False, blank=False)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    subpage_types = ['public.StandardPage']
        
    content_panels = Page.content_panels + [
        FieldPanel('description'),
        ImageChooserPanel('image'),
    ] + PublicBasePage.content_panels

    search_fields = PublicBasePage.search_fields + (
        index.SearchField('description'),
        index.SearchField('image'),
    )


class FloorPlanPage(PublicBasePage):
    """
    Floor plan page model.
    """ 
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    subpage_types = ['public.StandardPage']

    content_panels = Page.content_panels + [
        ImageChooserPanel('image'),
    ] + PublicBasePage.content_panels

    search_fields = PublicBasePage.search_fields + (
        index.SearchField('image'),
    )
