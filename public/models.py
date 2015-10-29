from django.db import models
from django import forms
from django.utils import timezone
from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailcore import blocks
from wagtail.wagtailadmin.edit_handlers import FieldPanel, FieldRowPanel, MultiFieldPanel, StreamFieldPanel, InlinePanel
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsearch import index
from modelcluster.fields import ParentalKey
from base.models import BasePage, DefaultBodyField, Address, Email, PhoneNumber

class StandardPage(BasePage):
    """
    A standard basic page.
    """
    body = DefaultBodyField()

    content_panels = Page.content_panels + [
        FieldPanel('description'),
        StreamFieldPanel('body'),
    ] + BasePage.content_panels


class LocationPageDonorPlacement(Orderable, models.Model):
    """
    Create a through table for linking donor pages to location pages
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


class LocationPage(BasePage, Email, Address, PhoneNumber):
    """
    Location and building pages.
    """
    # Model fields
    description = models.TextField(null=False, blank=False) 
    parent_building = models.ForeignKey('self',
        null=True, blank=True, on_delete=models.SET_NULL, limit_choices_to={'is_building': True})
    library_floorplan_link = models.URLField(max_length=200, blank=True, default='')
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
    is_24_hours = models.BooleanField(default=False)
    is_reservable = models.BooleanField(default=False)
    has_carrels = models.BooleanField(default=False)
    has_board = models.BooleanField(default=False)
    has_printing = models.BooleanField(default=False)
    has_soft_seating = models.BooleanField(default=False)
    has_cps = models.BooleanField(default=False)
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
        FieldPanel('description'),
        FieldPanel('parent_building'),
        FieldPanel('library_floorplan_link'),
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
            FieldPanel('is_24_hours', classname=ROW_CLASS),
            FieldPanel('is_reservable', classname=ROW_CLASS),
            FieldPanel('has_carrels', classname=ROW_CLASS),
            FieldPanel('has_board', classname=ROW_CLASS),
            FieldPanel('has_printing', classname=ROW_CLASS),
            FieldPanel('has_soft_seating', classname=ROW_CLASS),
            FieldPanel('has_cps', classname=ROW_CLASS),
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
    ] + Email.content_panels + Address.content_panels + BasePage.content_panels


class DonorPage(BasePage):
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
        
    content_panels = Page.content_panels + [
        FieldPanel('description'),
        ImageChooserPanel('image'),
    ] + BasePage.content_panels 
