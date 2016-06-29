from django.db import models
from django.db.models.fields import CharField
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
from base.models import PublicBasePage, DefaultBodyFields, Address, Email, PhoneNumber, SocialMediaFields, LinkBlock, RawHTMLBodyField
from datetime import date
from staff.models import StaffPage
from wagtail.wagtailimages.models import Image

import urllib

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
        required=False, help_text='Select a staff page from Loop/Staff', 
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

    # Search widget
    enable_search_widget = models.BooleanField(default=False)

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

    # Banner
    banner_title = models.CharField(max_length=100, blank=True)
    banner_image =  models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Banners should be approximately 1200 × 200 pixels"
    )

    subpage_types = ['public.StandardPage', 'public.LocationPage', 'public.DonorPage', \
        'lib_collections.CollectingAreaPage', 'lib_collections.CollectionPage', 'lib_collections.ExhibitPage', \
        'redirects.RedirectPage', 'units.UnitPage', 'ask_a_librarian.AskPage', 'units.UnitIndexPage', \
        'conferences.ConferenceIndexPage', 'base.IntranetPlainPage', 'dirbrowse.DirBrowsePage', \
        'public.StaffPublicPage', 'findingaids.FindingAidsPage', 'public.PublicRawHTMLPage']

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
    ] + PublicBasePage.content_panels

    widget_content_panels = [
        MultiFieldPanel(
            [
                FieldPanel('enable_search_widget')
            ],
            heading='Search Widget'
        ),
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
                ImageChooserPanel('banner_image'),
                FieldPanel('banner_title'),
            ],
            heading='Banner'
        ),
        MultiFieldPanel(
            [
                FieldPanel('events_feed_url'),
            ],
            heading='Workshops and Events'
        ),
       MultiFieldPanel(
            [
                FieldPanel('news_feed_url'),
                FieldPanel('active_tag'),
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
                PageChooserPanel('collection_page', 'lib_collections.CollectionPage'),
            ], 
            heading='Featured Collection'
        ),
        StreamFieldPanel('featured_library_expert_fallback'),
        StreamFieldPanel('featured_library_experts'),
    ] + SocialMediaFields.panels

    search_fields = PublicBasePage.search_fields + [
        index.SearchField('body', partial_match=True),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(PublicBasePage.promote_panels, heading='Promote'),
        ObjectList(Page.settings_panels, heading='Settings', classname="settings"),
        ObjectList(widget_content_panels, heading='Widgets'),
    ])


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


    def has_featured_lib_expert_fallback(self):
        """
        Test to see if a page has a "Featured 
        Library Expert" fallback set.

        Returns:
            Boolean
        """
        try:
            return self.streamblock_has_all_fields(
                self.featured_library_expert_fallback[0], 
                ['library_expert']
            ) and self.streamblock_has_link(self.featured_library_expert_fallback[0], 'libguides')
        except(IndexError):
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
        #print(self.featured_library_expert_fallback[0].value.get('library_expert'))
        today = date.today()
        for block in self.featured_library_experts:
            #print(block.value.get('library_expert'))
            has_fields = self.streamblock_has_all_fields(block, ['library_expert', 'start_date','end_date'])
            has_links = self.streamblock_has_link(block, 'libguides') # Could misfire, just an estimation
            in_range = block.value.get('start_date') <= today and block.value.get('end_date') >= today
            if (fallback and (has_fields and has_links)) and in_range:
                return (True, block)
        if (fallback):
            return (True, self.featured_library_expert_fallback[0])
        return (False, None)


    def unpack_lib_expert_block(self, block):
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

        Returns:
            Mixed dictionary with the following values: 
            person (StaffPage object), image (object), 
            profile (string url), links (list of html strings).
        """
        person = block.value.get('library_expert')
        libguides = block.value.get('libguides')
        image = person.specific.profile_picture
        profile = person.specific.public_page.url if person.specific.public_page else None
   
        links = [] 
        for guide in libguides:
            link_text = guide['link_text']
            url = guide['link_external'] if guide['link_external'] else guide['link_page']
            html = '<a href="%s">%s</a>' % (url, link_text)
            links.append(html)

        return {'person': person, 'image': image, 'profile': profile, 'links': links}


    def get_directory_link_by_location(self, location):
        """
        Return a link into the directory limited for a 
        given Library.

        Args:
            location: string, the building level locations 
            for which to retrieve a link into the public 
            directory.

        Returns:
            string, link into the public directory
            filtered by library.
        """
        base = '/about/directory/?view=staff&library='
        links = {'The John Crerar Library': base + urllib.parse.quote_plus('Crerar Library'),
                 'The D\'Angelo Law Library': base + urllib.parse.quote_plus('D\'Angelo Law Library'),
                 'The University of Chicago Library': '/about/directory/?view=staff',
                 'Eckhart Library': base + urllib.parse.quote_plus('Eckhart Library'),
                 'The Joe and Rika Mansueto Library': base + urllib.parse.quote_plus('Mansueto'),
                 'The Joseph Regenstein Library': base + urllib.parse.quote_plus('Regenstein Library'),
                 'Special Collections Research Center': base + urllib.parse.quote_plus('Special Collections Research Center'),
                 'Social Service Administration Library': base + urllib.parse.quote_plus('SSA Library')} 
        return links[location]


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
        
        has_featured_lib_expert = self.get_featured_lib_expert()[0]

        if has_featured_lib_expert:
            lib_expert_block = self.unpack_lib_expert_block(self.get_featured_lib_expert()[1])
            context['has_featured_lib_expert'] = has_featured_lib_expert
            context['featured_lib_expert'] = self.get_featured_lib_expert()[1]
            context['featured_lib_expert_name'] = lib_expert_block['person'] 
            context['featured_lib_expert_image'] = lib_expert_block['image']
            context['featured_lib_expert_profile'] = lib_expert_block['profile'] 
            context['featured_lib_expert_links'] = lib_expert_block['links']

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
    ] 

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(PublicBasePage.promote_panels, heading='Promote'),
        ObjectList(Page.settings_panels, heading='Settings', classname="settings"),
        ObjectList(widget_content_panels, heading='Widgets'),
    ])

    subpage_types = ['public.StandardPage', 'public.FloorPlanPage']

    search_fields = PublicBasePage.search_fields + [
        index.SearchField('short_description', partial_match=True),
        index.SearchField('long_description', partial_match=True),
        index.SearchField('parent_building'),
        index.SearchField('location_photo'),
        index.SearchField('reservation_display_url'),
        index.SearchField('reservation_display_text'),
    ]


    def features(self):
        """
        Boolean fields we use as "features" in the
        spaces browse and page display.

        Returns:
            List of tuples containing three strings where 
            the first item is a field name, the second item 
            is a display label and the third item is an 
            html icon for display. 
        """
        return [
                    ('is_quiet_zone', 'Quiet Zone', '<i class="fa fa-bell-slash-o"></i>'),
                    ('is_collaboration_zone', 'Collaboration Zone / Group study', '<i class="material-icons">people</i>'),
                    ('is_phone_zone', 'Cell Phone Zone', '<i class="material-icons">phone_android</i>'),
                    ('is_meal_zone', 'Meal Zone', '<i class="material-icons">local_dining</i>'),
                    ('is_open_space', 'Open Space', '<i class="material-icons">all_inclusive</i>'),
                    ('is_snacks_allowed', 'Snacks allowed', '<i class="material-icons">local_cafe</i>'),
                    ('is_24_hours', 'All Night Study', '<i class="material-icons">access_alarm</i>'),
                    ('has_printing', 'Copy / Print / Scan', '<i class="fa-print"></i>'),
                    ('has_public_computer', 'Public Computer(s)', '<i class="fa fa-desktop"></i>'),
                    ('has_dual_monitors', 'Dual Monitor stations', '<i class="material-icons">add_to_queue</i>'),
                    ('has_book_scanner', 'Overhead Book Scanner', '<i class="material-icons">import_contacts</i>'),
                    ('has_screen', 'Monitor/Projector', '<i class="material-icons">cast</i>'),
                    ('has_single_tables', 'Individual Tables', '<i class="material-icons">widgets</i>'),
                    ('has_large_tables', 'Large Tables', '<i class="material-icons">wb_iridescent</i>'),
                    ('has_carrels', 'Carrels', '<i class="material-icons">border_inner</i>'),
                    ('has_standing_desk', 'Standing Desks', '<i class="material-icons">accessibility</i>'),
                    ('has_soft_seating', 'Comfy Seating', '<i class="material-icons">weekend</i>'),
                    ('has_board', 'White Board', '<i class="material-icons">gesture</i>'),
                    ('is_reservable', 'Reservable', '<i class="fa fa-calendar-plus-o"></i>'),
                    ('is_no_food_allowed', 'No Food', ''),
                    ('has_lockers', 'Has Lockers', ''),
                    ('has_day_lockers', 'Has Day Lockers', ''),
                ]


    def has_any_features(self):
        """
        See if a location has fields, we've dubbed "features".

        Returns:
            Boolean
        """
        for item in self.features():
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
            for item in self.features():
                field = 'self.' + item[0]
                if eval(field):
                    html += '<li><a href="/spaces/?space_type=None&feature=%s">%s %s</a></li>' % (item[0], item[2], item[1])
            html += '</ul>'
            return html
        else:
            return ''


    @property
    def has_right_sidebar(self):
        """
        Test to see if a right sidebar should be 
        displayed.

        Returns:
            Boolean
        """
        return self.base_has_right_sidebar() or self.has_any_features()


    def get_context(self, request):
        """
        Override the page object's get context method.
        """
        context = super(LocationPage, self).get_context(request)
        context['features_html'] = self.get_features_html()

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
        ImageChooserPanel('image'),
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

    search_fields = PublicBasePage.search_fields + [
        index.SearchField('image'),
    ]


class StaffPublicPage(PublicBasePage):
    """
    A public page for staff members.
    """
    cnetid = CharField(
        max_length=255,
        blank=False,
        null=True)

    subpage_types = ['public.StandardPage']
    content_panels = Page.content_panels + [
        FieldPanel('cnetid')
    ] + PublicBasePage.content_panels

    def get_bio(self):
        """
        Gets the bio from a loop staff page.

        Returns:
            Streamfield or empty string.
        """
        try:
            return StaffPage.objects.live().filter(cnetid=self.cnetid)[0].bio
        except(IndexError):
            return ''

    def has_right_sidebar(self):
        return True

    def get_context(self, request):
        """
        Override the page object's get context method.
        """
        context = super(PublicBasePage, self).get_context(request)

        s = StaffPage.objects.get(cnetid=self.cnetid)
        v = s.vcards.first()

        cv = None
        if s.cv:
            cv = s.cv.file.url

        libguide_url = None
        if s.libguide_url:
            libguide_url = s.libguide_url

        expertises = []
        for expertise in s.expertise_placements.all():
            expertises.append(expertise.expertise.text)

        subjects = []
        for subject in s.staff_subject_placements.all():
            subjects.append(subject.subject)

        default_image = Image.objects.get(title="Default Placeholder Photo")

        context['bio'] = self.get_bio()
        context['breadcrumb_div_css'] = 'col-md-12 breadcrumbs hidden-xs hidden-sm'
        context['content_div_css'] = 'container body-container col-xs-12 col-lg-11 col-lg-offset-1'
        context['cv'] = cv
        context['default_image'] = default_image
        context['department_name'] = v.unit.name
        context['email'] = v.email
        context['expertises'] = expertises
        context['libguide_url'] = libguide_url
        context['library'] = v.unit.get_parent_library_name()
        context['orcid'] = s.orcid
        context['phone_number'] = v.phone_number
        context['profile_picture'] = s.profile_picture
        context['room_number'] = v.faculty_exchange.split(' ').pop()
        context['subjects'] = subjects
        context['vcardtitle'] = v.title
        return context


class PublicRawHTMLPage(PublicBasePage):
    """
    A public page for raw HTML.
    """
    html = StreamField(RawHTMLBodyField())

    content_panels = Page.content_panels + [
        StreamFieldPanel('html')
    ] + PublicBasePage.content_panels

