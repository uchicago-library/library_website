from django.db import models
from wagtail.wagtailcore.models import Page, Orderable
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


class ConferencePageMainRegistrationLinks(Orderable, AbstractButton):
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
    banner_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Banners should be 1200xB pixels"
    )
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

    subpage_types = ['conferences.ConferenceSubPage']

    search_fields = PublicBasePage.search_fields + (
        index.SearchField('subtitle'),
        index.SearchField('tagline'),
        index.SearchField('banner_image'),
        index.SearchField('branding_color'),
        index.SearchField('location'),
        index.SearchField('current'),
        index.SearchField('conference_logo'),
        index.SearchField('body'),
    )


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
