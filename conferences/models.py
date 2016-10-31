from django.db import models
from wagtail.wagtailcore.models import Page, Orderable, Site
from wagtail.wagtailcore.fields import StreamField
from base.models import PublicBasePage, AbstractButton, LinkedTextOrLogo, DefaultBodyFields, SocialMediaFields
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel, PageChooserPanel, MultiFieldPanel, StreamFieldPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from django.core.validators import RegexValidator
from wagtail.wagtailsearch import index
from modelcluster.fields import ParentalKey

# Through tables
class ConferencePageMainRegistrationLinks(Orderable, AbstractButton):
    """
    Creates a through table for the main 
    registration buttons on conference pages.
    """
    page = ParentalKey('conferences.ConferencePage', related_name='main_registration')
    
    class Meta:
        verbose_name = 'Main Registration Link'
        verbose_name_plural = 'Main Registration Links'


class ConferencePageSecondaryRegistrationLinks(Orderable, AbstractButton):
    """
    Creates a through table for the lesser 
    registration buttons on conference pages.
    """
    page = ParentalKey('conferences.ConferencePage', related_name='sub_registration')

    class Meta:
        verbose_name = 'Additional Registration Link'
        verbose_name_plural = 'Additional Registration Links'


class ConferencePageSponsors(Orderable, LinkedTextOrLogo):
    """
    Through table for sponsors.
    """
    page = ParentalKey('conferences.ConferencePage', related_name='sponsors')
    
    class Meta:
        verbose_name = 'Sponsor'
        verbose_name_plural = 'Sponsors'


class ConferencePageOrganizers(Orderable, LinkedTextOrLogo):
    """
    Through table for organizers.
    """
    page = ParentalKey('conferences.ConferencePage', related_name='organizers')
    
    class Meta:
        verbose_name = 'Sponsor'
        verbose_name_plural = 'Sponsors'


# Page definitions 
class ConferenceIndexPage(PublicBasePage):
    """
    Receptacle for all conference pages.
    """
    content_panels = Page.content_panels + PublicBasePage.content_panels
    subpage_types = ['conferences.ConferencePage']


class ConferencePage(PublicBasePage, SocialMediaFields):
    """
    Main page for creating conferences.
    """
    # Generic variables
    hex_regex = RegexValidator(regex='^#[a-zA-Z0-9]{6}$', \
        message='Please enter a hex color, e.g. #012043')

    # Field definitions
    primary_branding_color= models.CharField(validators=[hex_regex], \
        max_length=7, blank=True)
    secondary_branding_color= models.CharField(validators=[hex_regex], \
        max_length=7, blank=True)
    location = models.ForeignKey('public.LocationPage',
        null=True, blank=True, on_delete=models.SET_NULL, 
        related_name='%(app_label)s_%(class)s_related')
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    current = models.BooleanField(default=True, \
        help_text="Uncheck this when the conference has transpired")
    conference_logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    secondary_registration_heading = models.CharField(max_length=40, blank=True)
    secondary_registration_description = models.TextField(blank=True)
    body = StreamField(DefaultBodyFields())

    # Panels and subpage types
    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                ImageChooserPanel('banner_image'),
                FieldPanel('banner_title'),
                FieldPanel('banner_subtitle'),
            ],
            heading='Banner'
        ),
        MultiFieldPanel(
            [
                FieldPanel('primary_branding_color'),
                FieldPanel('secondary_branding_color'),
                ImageChooserPanel('conference_logo'),
            ],
            heading='Branding',
        ),
        MultiFieldPanel(
            [
                FieldPanel('start_date'),
                FieldPanel('end_date'),
            ],
            heading='Dates and Times',
        ),
        FieldPanel('location'),
        FieldPanel('current'),
        InlinePanel('main_registration', label='Main Registration Link'),
        MultiFieldPanel(
            [
                FieldPanel('secondary_registration_heading'),
                FieldPanel('secondary_registration_description'),
                InlinePanel('sub_registration', label='Secondary Registration Link'),
            ],
            heading='Secondary Registration Links',
        ),
        InlinePanel('sponsors', label='Sponsors'),
        InlinePanel('organizers', label='Organizers'),
        StreamFieldPanel('body'),
    ] + SocialMediaFields.panels + PublicBasePage.content_panels

    subpage_types = ['conferences.ConferenceSubPage', 'redirects.RedirectPage']

    search_fields = PublicBasePage.search_fields + [
        index.SearchField('banner_image'),
        index.SearchField('primary_branding_color'),
        index.SearchField('secondary_branding_color'),
        index.SearchField('location'),
        index.SearchField('current'),
        index.SearchField('conference_logo'),
        index.SearchField('body'),
    ]
    api_fields = ('body',)

    @property
    def has_right_sidebar(self):
        """
        Test to see if a right sidebar should be
        displayed.

        Returns:
            Boolean
        """
        fields = [self.sponsors, self.organizers, self.sub_registration, \
            self.secondary_registration_heading, self.secondary_registration_description]
        return self.base_has_right_sidebar() or self.has_field(fields)

    def has_conf_banner(self, current_site):
        """
        Used to override the boolean [0] value for PublicBasePage
        get_banner. 

        Args:
            current_site: object
        """
        return self.get_banner(current_site)[0] or (self.primary_branding_color and self.banner_title)

    def get_banner(self, current_site):
        """
        Override the default get_banner method so that
        banners will always display as long as a title
        is present.

        Args:
            current_site: site object.

        Returns:
            See get_banner in PublicBasePage. 
        """
        try:
            # Base case
            if self.banner_title:
                return (True, self.banner_image, self.banner_feature, self.banner_title, self.banner_subtitle, self.relative_url(current_site), self.title)
            # Recursive case
            else:
                return self.get_parent().specific.get_banner(current_site)
        # Reached the top of the tree (could factor this into an if)
        except(AttributeError):
            return (False, None, None, '', '', '', '')


    # Context
    def get_context(self, request):
        context = super(ConferencePage, self).get_context(request)
        current_site = Site.find_for_request(request)
        main_reg = self.main_registration.all()
        has_sidebar = self.has_left_sidebar(context) or bool(main_reg)
        context['has_left_sidebar'] = has_sidebar
        context['content_div_css'] = self.get_conditional_css_classes('content', has_sidebar)
        context['breadcrumb_div_css'] = self.get_conditional_css_classes('breadcrumbs', has_sidebar)
        context['has_banner'] = self.has_conf_banner(current_site)
        context['primary_branding_color'] = self.primary_branding_color
        context['secondary_branding_color'] = self.secondary_branding_color
        context['conference_logo'] = self.conference_logo
        context['conference_title'] = self.title
        context['has_social_media'] = self.has_social_media
        context['main_registration'] = main_reg
        context['sponsors'] = self.sponsors.all()
        context['organizers'] = self.organizers.all()
        context['secondary_registration'] = self.sub_registration.all()
        context['secondary_registration_heading'] = self.secondary_registration_heading
        context['secondary_registration_description'] = self.secondary_registration_description
        context['home'] = self.relative_url(current_site)
        return context

class ConferenceSubPage(PublicBasePage):
    """
    Subpages for conferences. These inherit 
    most of their template "goodness" from 
    parent ConferencePage.
    """
    body = StreamField(DefaultBodyFields())

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
    ] + PublicBasePage.content_panels

    subpage_types = ['conferences.ConferenceSubPage']

    search_fields = PublicBasePage.search_fields + [
        index.SearchField('body'),
    ]

    api_fields = ('body',)

    @property
    def has_right_sidebar(self):
        """
        Override default test to see if a right 
        sidebar should be displayed.

        Returns:
            Boolean
        """
        parent = self.get_parent_of_type('conference page')
        return parent.has_right_sidebar

    @property
    def has_social_media(self):
        """
        Override default test for social media.

        Returns:
            Boolean
        """
        parent = self.get_parent_of_type('conference page')
        return parent.has_social_media

    # Context
    def get_context(self, request):
        context = super(ConferenceSubPage, self).get_context(request)
        current_site = Site.find_for_request(request)
        parent = self.get_parent_of_type('conference page')
        has_sidebar = parent.has_left_sidebar(context) or bool(main_reg)

        # Set social media fields dynamically and
        # get all the values from the parent page.
        # This doesn't seem like a good practice
        # How else can this be done?
        social_media_fields = [f.name for f in SocialMediaFields._meta.get_fields()]
        for field in social_media_fields:
            exec('self.' + field + ' = ' + 'parent.' + field)

        context['primary_branding_color'] = parent.primary_branding_color
        context['secondary_branding_color'] = parent.secondary_branding_color
        context['conference_logo'] = parent.conference_logo 
        context['conference_title'] = parent.title
        context['has_social_media'] = parent.has_social_media
        context['main_registration'] = parent.main_registration.all()
        context['sponsors'] = parent.sponsors.all()
        context['organizers'] = parent.organizers.all()
        context['secondary_registration'] = parent.sub_registration.all()
        context['secondary_registration_heading'] = parent.secondary_registration_heading
        context['secondary_registration_description'] = parent.secondary_registration_description
        context['home'] = parent.relative_url(current_site)
        return context
