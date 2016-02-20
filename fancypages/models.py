from django.db import models
from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailcore import blocks
from wagtail.wagtailadmin.edit_handlers import FieldPanel, FieldRowPanel, MultiFieldPanel, StreamFieldPanel, InlinePanel
from wagtail.wagtailsearch import index
from base.models import PublicBasePage, DefaultBodyFields


class FancyPage(PublicBasePage):
    """
    Fancy page type for department and other special pages.
    """
    body = StreamField(DefaultBodyFields())

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
    ] + PublicBasePage.content_panels

