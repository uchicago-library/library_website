from datetime import date
from urllib.parse import quote

from base.models import (
    Address, CarouselItem, DefaultBodyFields, Email, IconLinkItem, LinkBlock,
    PhoneNumber, PublicBasePage, RawHTMLBlock, RawHTMLBodyField,
    ReusableContentBlock, SocialMediaFields
)
from base.utils import unfold
from django.db import models
from django.db.models.fields import CharField
from modelcluster.fields import ParentalKey
from staff.models import StaffPage
from staff.utils import libcal_id_by_email
from subjects.utils import get_subjects_html
from units.models import BUILDINGS, UnitIndexPage
from wagtail.admin.panels import (
    FieldPanel, FieldRowPanel, HelpPanel, InlinePanel, MultiFieldPanel,
    ObjectList, PageChooserPanel, TabbedInterface
)
from wagtail.api import APIField
from wagtail import blocks
from wagtail.blocks import RichTextBlock
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable, Page, Site
from wagtail.images.models import Image
from wagtail.search import index

from public.utils import get_features

from units.utils import get_default_unit

# TEMPORARY: Fix issue # 2267:https://github.com/torchbox/wagtail/issues/2267
# from wagtail.admin.forms import WagtailAdminPageForm
# from wagtail.admin.panels import TabbedInterface as OriginalTabbedInterface
# class TabbedInterface(OriginalTabbedInterface):
#
#    def __init__(self, children, base_form_class=WagtailAdminPageForm):
#        super().__init__(children, base_form_class)


class FeaturedLibraryExpertBaseBlock(blocks.StructBlock):
    """
    Base streamfield block for "Featured Library Experts".
    """
    library_expert = blocks.PageChooserBlock(  # In the future Wagtail plans to allow the limiting of PageChooserBlock by page type. This will improve when we have that.
        required=False, help_text='Be sure to select a StaffPage (not a StaffPublicPage)',
    )
    libguides = blocks.ListBlock(LinkBlock(), icon='link')


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


class StandardPageSidebarReusableContent(Orderable, models.Model):
    """
    Repeatable, reusable content widget for sidebar
    """
    page = ParentalKey(
        'public.StandardPage',
        on_delete=models.CASCADE,
        related_name='reusable_content'
    )
    content = models.ForeignKey(
        'reusable_content.ReusableContent',
        default=None,
        on_delete=models.CASCADE,
        related_name='+'
    )

    class Meta:
        verbose_name = "Content"
        verbose_name_plural = "Content"

    panels = [
        FieldPanel('content'),
    ]


class StandardPageCarouselItem(Orderable, CarouselItem):
    """
    Carousel widgets for standard pages
    """
    page = ParentalKey('public.StandardPage', related_name='carousel_items')


class StandardPageIconLinkItem(Orderable, IconLinkItem):
    """
    Custom icon links widget for standard pages
    """
    page = ParentalKey('public.StandardPage', related_name='icon_link_items')


class StandardPage(PublicBasePage, SocialMediaFields):
    """
    A standard basic page.
    """
    # Page content
    body = StreamField(
        DefaultBodyFields(),
        blank=True,
    )

    # Search widget
    enable_search_widget = models.BooleanField(default=False)

    # Find spaces fields
    enable_find_spaces = models.BooleanField(default=False)
    book_a_room_link = models.URLField(max_length=255, blank=True, default='')

    # Custom icons fields
    widget_title = models.CharField(max_length=100, blank=True)
    more_icons_link = models.URLField(
        max_length=255, blank=True, default='', verbose_name='View More Link'
    )
    more_icons_link_label = models.CharField(
        max_length=100, blank=True, verbose_name='View More Link Label'
    )

    # Featured collections
    collection_page = models.ForeignKey(
        'lib_collections.CollectionPage',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL
    )

    # Featured Library Expert
    featured_library_expert_fallback = StreamField(
        FeaturedLibraryExpertBaseFields(required=False),
        blank=True,
        default=[],
    )

    expert_link = models.CharField(
        max_length=400, default="/about/directory/?view=staff", verbose_name="Featured Expert Link"
    )

    featured_library_experts = StreamField(
        FeaturedLibraryExpertFields(required=False),
        blank=True,
        default=[],
    )

    subpage_types = [
        'alerts.AlertIndexPage',
        'public.StandardPage',
        'public.LocationPage',
        'public.DonorPage',
        'lib_collections.CollectingAreaPage',
        'lib_collections.CollectionPage',
        'lib_collections.ExhibitPage',
        'lib_news.LibNewsIndexPage',
        'redirects.RedirectPage',
        'units.UnitPage',
        'ask_a_librarian.AskPage',
        'units.UnitIndexPage',
        'conferences.ConferenceIndexPage',
        'base.IntranetPlainPage',
        'dirbrowse.DirBrowsePage',
        'public.StaffPublicPage',
    ]

    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ] + PublicBasePage.content_panels

    widget_content_panels = [
        MultiFieldPanel(
            [FieldPanel('enable_search_widget')], heading='Search Widget'
        ),
        MultiFieldPanel(
            [
                FieldPanel('quicklinks_title'),
                FieldPanel('quicklinks'),
                FieldPanel('view_more_link_label'),
                FieldPanel('view_more_link'),
                FieldPanel('change_to_callout'),
            ],
            heading='Quicklinks'
        ),
        MultiFieldPanel(
            [
                FieldPanel('enable_index'),
                FieldPanel('display_hierarchical_listing'),
            ],
            heading='Auto-generated Sitemap'
        ),
        MultiFieldPanel(
            [
                FieldPanel('display_hours_in_right_sidebar'),
            ],
            heading='Granular hours'
        ),
        MultiFieldPanel(
            [
                FieldPanel('banner_image'),
                FieldPanel('banner_title'),
            ],
            heading='Banner'
        ),
        MultiFieldPanel(
            [
                FieldPanel('events_feed_url'),
            ], heading='Workshops and Events'
        ),
        MultiFieldPanel(
            [
                FieldPanel('news_feed_source'),
                FieldPanel('external_news_page'),
                PageChooserPanel('internal_news_page'),
            ],
            heading='News'
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
                PageChooserPanel(
                    'collection_page', 'lib_collections.CollectionPage'
                ),
            ],
            heading='Featured Collection'
        ),
        MultiFieldPanel(
            [
                FieldPanel('rich_text_heading'),
                FieldPanel('rich_text'),
                PageChooserPanel('rich_text_link'),
                FieldPanel('rich_text_external_link'),
                FieldPanel('rich_text_link_text'),
                FieldPanel('link_queue'),
            ],
            heading='Rich Text'
        ),
        InlinePanel('carousel_items', label='Carousel items'),
        MultiFieldPanel(
            [
                FieldPanel('widget_title'),
                InlinePanel(
                    'icon_link_items', max_num=3, label='Icon Link items'
                ),
                FieldPanel('more_icons_link'),
                FieldPanel('more_icons_link_label'),
            ],
            heading='Custom Icon Links'
        ),
        InlinePanel('reusable_content', label='Reusable Content Blocks'),
        FieldPanel('expert_link'),
        FieldPanel('featured_library_expert_fallback'),
        FieldPanel('featured_library_experts'),
        MultiFieldPanel(
            [
                FieldPanel('cgi_mail_form_thank_you_text'),
                FieldPanel('cgi_mail_form'),
            ],
            heading='CGIMail Form'
        ),
    ] + SocialMediaFields.panels

    search_fields = PublicBasePage.search_fields + [
        index.AutocompleteField('body'),
        index.FilterField('exclude_from_site_search'),
    ]

    promote_fields = PublicBasePage.promote_panels + [
        MultiFieldPanel(
            [
                FieldPanel('exclude_from_search_engines'),
                FieldPanel('exclude_from_site_search'),
                FieldPanel('exclude_from_sitemap_xml'),
            ], heading='Exclude Fields'
        ),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading='Content'),
            ObjectList(promote_fields, heading='Promote'),
            ObjectList(
                Page.settings_panels, heading='Settings', classname="settings"
            ),
            ObjectList(widget_content_panels, heading='Widgets'),
        ]
    )

    def streamblock_has_link(self, streamblock, field):
        """
        Check that a streamfield block object has a
        either an internal or external link when
        base.models.LinkBlock is in use.

        Args:
            streamblock: streamfield block object,
            wagtail.blocks.stream_block.StreamValue.StreamChild.

            field: string field name that contains
            a ListBlock of LinkBlocks.
        """
        block_list = streamblock.value.get(field)
        for block in block_list:
            val1 = block.get('link_text')
            val2 = block.get('link_external')
            val3 = block.get('link_page')
            if not (val1 and val2) and not (val1 and val3):
                return False
        return True

    def streamblock_has_all_fields(self, streamblock, field_list):
        """
        Test to see if a streamfield block has a value for all
        fields in a given list.

        Args:
            streamblock: streamfield block object,
            wagtail.blocks.stream_block.StreamValue.StreamChild.

            field_names: list of strings, field names.

        Returns:
            Boolean
        """
        for field in field_list:
            value = streamblock.value.get(field)
            if not value:
                return False
        return True

    def has_featured_lib_expert_fallback(self):
        """
        Test to see if a page has a "Featured
        Library Expert" fallback set.

        Returns:
            Boolean
        """
        try:
            return self.streamblock_has_all_fields(
                self.featured_library_expert_fallback[0], ['library_expert']
            ) and self.streamblock_has_link(
                self.featured_library_expert_fallback[0], 'libguides'
            )
        except (IndexError):
            return False

    def get_featured_lib_expert(self):
        """
        Test to see if a page has a "Featured Library Expert".
        Return a boolean and the featured library expert for
        today's date. Return False and None if there is no
        Featured Library Expert for today. The fallback is
        used if nothing is available for today's date. In
        order to return True a proper fallback must always
        be set.

        Returns:
            A mixed tuple where the first value is a boolean
            and the second value is a streamfield block or
            None when the first value is False.
        """
        fallback = self.has_featured_lib_expert_fallback()
        # print(self.featured_library_expert_fallback[0].value.get('library_expert'))
        today = date.today()
        for block in self.featured_library_experts:
            # print(block.value.get('library_expert'))
            has_fields = self.streamblock_has_all_fields(
                block, ['library_expert', 'start_date', 'end_date']
            )
            # Could misfire, just an estimation
            has_links = self.streamblock_has_link(block, 'libguides')
            in_range = block.value.get(
                'start_date'
            ) <= today and block.value.get('end_date') >= today
            if (fallback and (has_fields and has_links)) and in_range:
                return (True, block)
        if (fallback):
            return (True, self.featured_library_expert_fallback[0])
        return (False, None)

    def unpack_lib_expert_block(self, block, current_site):
        """
        Unpack the values from a "Featured Library Expert"
        streamfield block and return a data structure for
        display in the templates. This method wouldn't be
        needed, however, at the moment Wagtail doesn't allow
        for getting the page context from a block. This is
        discussed in Wagtail github issue #s 1743 and 2469.
        When a solution is implemented in the Wagtail base
        we could get rid of this.

        Args:
            block: Featured Library Expert or fallback
            streamfield block.

            current_site: Wagtail site object for the
            request.

        Returns:
            Mixed dictionary with the following values:
            person (StaffPage object), image (object),
            profile (string url), links (list of html strings).
        """
        person = block.value.get('library_expert')
        libguides = block.value.get('libguides')
        image = person.specific.profile_picture
        email = person.specific.staff_page_email.first().email
        try:
            public_person = StaffPublicPage.objects.get(title=str(person))
        except:
            public_person = None
        profile = public_person.relative_url(
            current_site
        ) if public_person else None

        links = []
        for guide in libguides:
            link_text = guide['link_text']
            url = guide['link_external'] if guide['link_external'] else guide[
                'link_page'].relative_url(current_site)
            html = '<a href="%s">%s</a>' % (url, link_text)
            links.append(html)

        return {
            'person': person,
            'image': image,
            'profile': profile,
            'links': links,
            'email': email
        }

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
    def has_icon_link_items(self):
        """
        Determine if there is a "Link Items"
        widget on the page.
        Returns:
            Boolean
        """
        if self.has_field([self.icon_link_items]):
            return self.icon_link_items.all().count() > 0
        return False

    @property
    def has_right_sidebar(self):
        """
        Determine if a right sidebar should
        be displayed in the template.

        Returns:
            boolean
        """
        fields = [self.collection_page]
        if self.base_has_right_sidebar():
            return True
        elif self.has_social_media:
            return True
        elif self.has_find_spaces:
            return True
        else:
            return self.has_field(fields)

    def get_context(self, request):
        """
        Override the page object's get context method.
        """
        context = super(StandardPage, self).get_context(request)
        current_site = Site.find_for_request(request)
        has_featured_lib_expert = self.get_featured_lib_expert()[0]

        if has_featured_lib_expert:
            lib_expert_block = self.unpack_lib_expert_block(
                self.get_featured_lib_expert()[1], current_site
            )
            has_libcal_schedule = libcal_id_by_email(
                lib_expert_block['email']
            ) != ''
            context['has_featured_lib_expert'] = has_featured_lib_expert
            context['has_libcal_schedule'] = has_libcal_schedule
            context['featured_lib_expert'] = self.get_featured_lib_expert()[1]
            context['featured_lib_expert_name'] = lib_expert_block['person']
            context['featured_lib_expert_image'] = lib_expert_block['image']
            context['featured_lib_expert_profile'] = lib_expert_block['profile']
            context['featured_lib_expert_links'] = lib_expert_block['links']
            context['email'] = lib_expert_block['email']

        context['has_search_widget'] = self.enable_search_widget

        return context


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
    page_alerts = StreamField(
        [
            ('paragraph', RichTextBlock()),
            ('reusable_content_block', ReusableContentBlock()),
            ('html', RawHTMLBlock()),
        ],
        null=True,
        blank=True,
    )
    long_description = RichTextField(null=False, blank=False)
    parent_building = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        limit_choices_to={'is_building': True}
    )
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
    is_special_use = models.BooleanField(default=False)
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
    has_all_gender_restrooms = models.BooleanField(default=False)

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
        FieldPanel('location_photo'),
        FieldRowPanel(
            [
                FieldPanel('is_building'),
                FieldPanel('is_phone_zone'),
                FieldPanel('is_collaboration_zone'),
                FieldPanel('is_meal_zone'),
                FieldPanel('is_quiet_zone'),
                FieldPanel('is_study_space'),
                FieldPanel('is_teaching_space'),
                FieldPanel('is_event_space'),
                FieldPanel('is_special_use'),
                FieldPanel('is_open_space'),
                FieldPanel('is_24_hours'),
                FieldPanel('is_reservable'),
                FieldPanel('has_carrels'),
                FieldPanel('has_board'),
                FieldPanel('has_printing'),
                FieldPanel('has_soft_seating'),
                FieldPanel('has_dual_monitors'),
                FieldPanel('has_single_tables'),
                FieldPanel('has_large_tables'),
                FieldPanel('has_screen'),
                FieldPanel('has_natural_light'),
                FieldPanel('is_no_food_allowed'),
                FieldPanel('has_book_scanner'),
                FieldPanel('has_public_computer'),
                FieldPanel('is_snacks_allowed'),
                FieldPanel('has_standing_desk'),
                FieldPanel('has_lockers'),
                FieldPanel('has_day_lockers'),
                FieldPanel('has_all_gender_restrooms'),
            ], classname='location-booleans'
        ),
        MultiFieldPanel(PhoneNumber.content_panels, heading='Phone Number'),
        InlinePanel('location_donor_page_placements', label='Donor'),
    ] + Email.content_panels + Address.content_panels + PublicBasePage.content_panels

    widget_content_panels = [
        FieldPanel('page_alerts'),
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
                FieldPanel('display_hours_in_right_sidebar'),
            ],
            heading='Granular hours'
        ),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading='Content'),
            ObjectList(PublicBasePage.promote_panels, heading='Promote'),
            ObjectList(
                Page.settings_panels, heading='Settings', classname="settings"
            ),
            ObjectList(widget_content_panels, heading='Widgets'),
        ]
    )

    subpage_types = ['public.StandardPage', 'public.FloorPlanPage']

    def mk_search_field(self):
        return ' '.join(i[0] for i in get_features())

    search_fields = PublicBasePage.search_fields + [
        index.AutocompleteField('short_description'),
        index.AutocompleteField('long_description'),
        index.SearchField('parent_building'),
        index.SearchField('location_photo'),
        index.SearchField('reservation_url'),
        index.SearchField('mk_search_field'),
    ]

    api_fields = [
        APIField('libcal_library_id'),
        APIField('google_map_link'),
        APIField('reservation_url'),
    ]

    def has_any_features(self):
        """
        See if a location has fields, we've dubbed "features".

        Returns:
            Boolean
        """
        for item in get_features():
            field = 'self.' + item[0]
            if eval(field):
                return True
        return False

    @property
    def has_features(self):
        """
        Convenience wrapper for has_any_features.
        This is to be used in the templates.

        Returns:
            Boolean
        """
        return self.has_any_features()

    def get_features_html(self):
        """
        Generate html for the display of "features"
        on location pages.

        Returns:
            Html or an empty string
        """
        html = '<ul class="features-list">'
        if self.has_any_features():
            for item in get_features():
                field = 'self.' + item[0]
                if eval(field):
                    html += '<li><a href="/spaces/?space_type=None&feature=%s">%s %s</a></li>' % (
                        item[0], item[2], item[1]
                    )
            html += '</ul>'
            return html
        else:
            return ''

    @property
    def features_html(self):
        """
        Convenience property to use in templates
        and custom views.

        Returns:
            string, html
        """
        return self.get_features_html()

    @property
    def has_right_sidebar(self):
        """
        Test to see if a right sidebar should be
        displayed.

        Returns:
            Boolean
        """
        self.has_floorplans()
        return self.base_has_right_sidebar() or self.has_any_features(
        ) or self.has_floorplans

    def has_floorplans(self):
        """
        Detect if a location page has floorplans.

        Returns:
            boolean
        """
        objects = self.location_floor_placements.get_live_query_set().filter(
            parent_id=self.id
        )
        for obj in objects:
            if obj.floor_id:
                return True
        return False

    def get_context(self, request):
        """
        Override the page object's get context method.
        """
        context = super(LocationPage, self).get_context(request)

        default_image = Image.objects.get(title="Default Placeholder Photo")

        context['default_image'] = default_image
        context['features_html'] = self.get_features_html()
        context['has_floorplans'] = self.has_floorplans()

        return context


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
        FieldPanel('image'),
    ] + PublicBasePage.content_panels

    search_fields = PublicBasePage.search_fields + [
        index.SearchField('description'),
        index.SearchField('image'),
    ]


class FloorPlanPage(PublicBasePage):
    """
    Floor plan page model.
    """

    def __str__(self):
        return '%s, %s' % (self.title, self.unit.location.parent_building)

    intro = RichTextField(null=True, blank=True)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    subpage_types = ['public.StandardPage']

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('image'),
    ] + PublicBasePage.content_panels

    search_fields = PublicBasePage.search_fields + [
        index.SearchField('image'),
    ]


class StaffPublicPage(PublicBasePage):
    """
    A public page for staff members.
    """
    cnetid = CharField(max_length=255, blank=False, null=True)

    subpage_types = ['public.StandardPage']
    content_panels = Page.content_panels + [
        HelpPanel(
            heading='Editing your staff page',
            template='public/blocks/staffpage_helppanel.html',
        ),
        FieldPanel('cnetid')
    ] + PublicBasePage.content_panels

    def get_staff_page_id(self):
        """
        Gets the page ID from a loop staff page.

        Returns:
            ID or empty string.
        """
        try:
            return StaffPage.objects.all().filter(cnetid=self.cnetid)[0].id
        except (IndexError):
            return ''

    def get_bio(self):
        """
        Gets the bio from a loop staff page.

        Returns:
            Streamfield or empty string.
        """
        try:
            return StaffPage.objects.live().filter(cnetid=self.cnetid)[0].bio
        except (IndexError):
            return ''

    def has_right_sidebar(self):
        return True

    def get_context(self, request):
        """
        Override the page object's get context method.
        """
        context = super(StaffPublicPage, self).get_context(request)

        s = StaffPage.objects.get(cnetid=self.cnetid)

        try:
            cv = s.cv.file.url
        except AttributeError:
            cv = ''

        expertises = []
        for expertise in s.expertise_placements.all():
            expertises.append(expertise.expertise.text)

        libguide_url = s.libguide_url

        default_image = Image.objects.get(title="Default Placeholder Photo")

        try:
            department_name = s.staff_page_units.first().library_unit.title
        except AttributeError:
            department_name = None

        try:
            department_full_name = s.staff_page_units.first(
            ).library_unit.get_full_name()
        except AttributeError:
            department_full_name = None

        try:
            email = s.staff_page_email.first().email
        except AttributeError:
            email = None

        try:
            building_int = s.staff_page_units.first().library_unit.building
            building_str = list(
                filter(lambda b: b[0] == building_int, BUILDINGS)
            )[0][1]
        except AttributeError:
            building_str = None

        def next_unit(unit):
            if isinstance(unit.specific, UnitIndexPage):
                return False
            else:
                return (unit, unit.get_parent())

        unit = get_default_unit()
        try:
            unit = s.staff_page_units.first().library_unit
        except AttributeError:
            pass

        parent_unit_list = [u.title for u in unfold(next_unit, unit)]

        parent_unit_list.reverse()

        parent_units = {u.title: "" for u in unfold(next_unit, unit)}

        index = 1

        while index < len(parent_unit_list):
            parent_unit_list[index] = parent_unit_list[
                index - 1] + " - " + parent_unit_list[index]
            index += 1

        parent_unit_list.reverse()

        second_index = 0

        for u in parent_units:
            parent_units[u] = quote(
                parent_unit_list[second_index].encode('utf8')
            )
            second_index += 1

        context.update(
            {
                'bio': self.get_bio(),
                'breadcrumb_div_css':
                'col-md-12 breadcrumbs hidden-xs hidden-sm',
                'content_div_css':
                'container body-container col-xs-12 col-lg-11 col-lg-offset-1',
                'cv': cv,
                'default_image': default_image,
                'department_name': department_name,
                'department_full_name': department_full_name,
                'email': email,
                'expertises': expertises,
                'libguide_url': libguide_url,
                'library': building_str,
                'orcid': s.orcid,
                'profile_picture': s.profile_picture,
                'staff_page': s,
                'subjects': get_subjects_html(s.staff_subject_placements.all()),
                'positiontitle': s.position_title,
                'parent_units': parent_units
            }
        )
        return context

    search_fields = PublicBasePage.search_fields + [
        index.SearchField('cnetid'),
    ]


class PublicRawHTMLPage(PublicBasePage):
    """
    A public page for raw HTML.
    """
    html = StreamField(
        RawHTMLBodyField(),
    )

    content_panels = Page.content_panels + [
        FieldPanel('html')
    ] + PublicBasePage.content_panels

    widget_content_panels = [
        MultiFieldPanel(
            [
                FieldPanel('cgi_mail_form_thank_you_text'),
                FieldPanel('cgi_mail_form'),
            ],
            heading='CGIMail Form'
        ),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading='Content'),
            ObjectList(PublicBasePage.promote_panels, heading='Promote'),
            ObjectList(
                Page.settings_panels, heading='Settings', classname="settings"
            ),
            ObjectList(widget_content_panels, heading='Widgets'),
        ]
    )

    search_fields = PublicBasePage.search_fields + [
        index.AutocompleteField('html'),
    ]

    subpage_types = ['public.StandardPage', 'public.PublicRawHTMLPage']
