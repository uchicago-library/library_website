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
    subtitle = models.CharField(max_length=100, blank=True) 
    tagline = models.CharField(max_length=150, blank=True)
    branding_color= models.CharField(validators=[hex_regex], \
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
                FieldPanel('subtitle'),
                FieldPanel('tagline'),
            ],
            heading='Additional Title Info'
        ),
        MultiFieldPanel(
            [
                ImageChooserPanel('banner_image'),
                FieldPanel('branding_color'),
                ImageChooserPanel('conference_logo'),
            ],
            heading='Branding',
            classname='collapsible collapsed'
        ),
        MultiFieldPanel(
            [
                FieldPanel('start_date'),
                FieldPanel('end_date'),
            ],
            heading='Dates and Times',
            classname='collapsible collapsed'
        ),
        FieldPanel('location', classname='collapsible collapsed multi-field'),
        FieldPanel('current'),
        InlinePanel('main_registration', label='Main Registration Link'),
        MultiFieldPanel(
            [
                FieldPanel('secondary_registration_heading'),
                FieldPanel('secondary_registration_description'),
                InlinePanel('sub_registration', label='Secondary Registration Link'),
            ],
            heading='Secondary Registration Links',
            classname='collapsible collapsed'
        ),
        InlinePanel('sponsors', label='Sponsors'),
        InlinePanel('organizers', label='Organizers'),
        StreamFieldPanel('body'),
    ] + SocialMediaFields.panels + PublicBasePage.content_panels

    subpage_types = ['conferences.ConferenceSubPage', 'redirects.RedirectPage']

    search_fields = PublicBasePage.search_fields + [
        index.SearchField('subtitle'),
        index.SearchField('tagline'),
        index.SearchField('banner_image'),
        index.SearchField('branding_color'),
        index.SearchField('location'),
        index.SearchField('current'),
        index.SearchField('conference_logo'),
        index.SearchField('body'),
    ]
    api_fields = ('body',)

    # Context
    def get_context(self, request):
        context = super(ConferencePage, self).get_context(request)
        current_site = Site.find_for_request(request)
        context['banner_image'] = self.banner_image
        context['branding_color'] = self.branding_color
        context['conference_logo'] = self.conference_logo
        context['conference_title'] = self.title
        context['conference_subtitle'] = self.subtitle
        context['conference_tagline'] = self.tagline
        context['has_social_media'] = self.has_social_media
        context['main_registration'] = self.main_registration.all()
        context['sponsors'] = self.sponsors.all()
        context['organizers'] = self.organizers.all()
        context['twitter_page'] = self.twitter_page 
        context['facebook_page'] = self.facebook_page
        context['hashtag_page'] = self.hashtag_page
        context['hashtag'] = self.hashtag
        context['instagram_page'] = self.instagram_page
        context['youtube_page'] = self.youtube_page
        context['blog_page'] = self.blog_page
        context['tumblr_page'] = self.tumblr_page
        context['snapchat_page'] = self.snapchat_page
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


    # Context
    def get_context(self, request):
        context = super(ConferenceSubPage, self).get_context(request)
        current_site = Site.find_for_request(request)
        context['banner_image'] = self.get_parent().conferencepage.banner_image
        context['branding_color'] = self.get_parent().conferencepage.branding_color
        context['conference_logo'] = self.get_parent().conferencepage.conference_logo 
        context['conference_title'] = self.get_parent().title
        context['conference_subtitle'] = self.get_parent().conferencepage.subtitle
        context['conference_tagline'] = self.get_parent().conferencepage.tagline
        context['has_social_media'] = self.get_parent().conferencepage.has_social_media
        context['main_registration'] = self.get_parent().conferencepage.main_registration.all()
        context['sponsors'] = self.get_parent().conferencepage.sponsors.all()
        context['organizers'] = self.get_parent().conferencepage.organizers.all()
        context['twitter_page'] = self.get_parent().conferencepage.twitter_page 
        context['facebook_page'] = self.get_parent().conferencepage.facebook_page
        context['hashtag_page'] = self.get_parent().conferencepage.hashtag_page
        context['hashtag'] = self.get_parent().conferencepage.hashtag
        context['instagram_page'] = self.get_parent().conferencepage.instagram_page
        context['youtube_page'] = self.get_parent().conferencepage.youtube_page
        context['blog_page'] = self.get_parent().conferencepage.blog_page
        context['tumblr_page'] = self.get_parent().conferencepage.tumblr_page
        context['snapchat_page'] = self.get_parent().conferencepage.snapchat_page
        context['secondary_registration'] = self.get_parent().conferencepage.sub_registration.all()
        context['secondary_registration_heading'] = self.get_parent().conferencepage.secondary_registration_heading
        context['secondary_registration_description'] = self.get_parent().conferencepage.secondary_registration_description
        context['home'] = self.get_parent().conferencepage.relative_url(current_site)
        return context
