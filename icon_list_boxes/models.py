from django.db import models
from wagtail.wagtailcore.blocks import StructBlock, StreamBlock, FieldBlock, CharBlock, ListBlock, PageChooserBlock, RichTextBlock
from wagtail.wagtaildocs.blocks import DocumentChooserBlock
from base.models import LinkFields
from wagtail.wagtailadmin.edit_handlers import FieldPanel, PageChooserPanel, StreamFieldPanel
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel

class IconListBlock(StructBlock):
    """
    A streamfield for aesthetically pleasing 
    lists of links with an icon and heading.
    """
    icon = CharBlock(help_text="Add a Font Awesome icon name here")
    heading = CharBlock()
    text = RichTextBlock()

    class Meta:
        icon = 'snippet'
        template = 'intranettocs/blocks/icon_list.html'


class IconListCluster(StreamBlock):
    """
    Standard default streamfield options to be shared
    across content types.
    """
    list_block = IconListBlock()
