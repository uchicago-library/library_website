from django.db import models
from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailcore.blocks import CharBlock, ListBlock, RichTextBlock
from base.models import BasePage
from icon_list_boxes.models import IconListBlock, IconListCluster
from wagtail.wagtailadmin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.wagtailsearch import index

class TOCPage(BasePage):
    """
    Table of Contents Pages for the intranet.
    """
    body = StreamField(IconListCluster())

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
    ] + BasePage.content_panels

    subpage_types = ['base.IntranetIndexPage', 'base.IntranetPlainPage', 'intranettocs.TOCPage']
    
    search_fields = BasePage.search_fields + (
        index.SearchField('body'),
    )
