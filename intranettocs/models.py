from django.db import models
from wagtail.core.models import Page
from wagtail.core.fields import StreamField
from wagtail.core.blocks import CharBlock, ListBlock, RichTextBlock
from base.models import BasePage
from icon_list_boxes.models import IconListBlock, IconListCluster
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.search import index

class TOCPage(BasePage):
    """
    Table of Contents Pages for the intranet.
    """
    body = StreamField(IconListCluster())

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
    ] + BasePage.content_panels

    subpage_types = ['base.IntranetIndexPage', 'base.IntranetPlainPage', 'intranettocs.TOCPage']
    
    search_fields = BasePage.search_fields + [
        index.SearchField('body'),
    ]
