from django.db import models
from django import forms
from django.utils import timezone
from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailcore import blocks
from wagtail.wagtailadmin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtailsearch import index
from base.models import BasePage

class StandardPage(BasePage):
    """
    A standard basic page.
    """
    body = StreamField([
        ('heading', blocks.CharBlock(classname="full title", icon='title')),
        ('paragraph', blocks.RichTextBlock(icon='pilcrow')),
        ('image', ImageChooserBlock(icon='image / picture')),
    ])

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
        FieldPanel('location'),
    ]

class LocationPage(BasePage):
    """
    Location and building pages.
    """
    # Model fields 
    name = models.CharField(max_length=45, blank=False)
    is_building = models.BooleanField(default=False)

    # Set what appears in the admin
    content_panels = Page.content_panels + [
        FieldPanel('name'),
        FieldPanel('is_building'),
    ]
