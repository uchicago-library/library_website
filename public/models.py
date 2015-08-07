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

StandardPage.content_panels += [
    StreamFieldPanel('body'),
]
