from django.db import models
from django.db.models import F
from wagtail.wagtailcore.blocks import StructBlock, StreamBlock, FieldBlock, CharBlock, ListBlock, PageChooserBlock, RichTextBlock
from wagtail.wagtailcore.models import Page
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


class IconAutoListBlock(StructBlock):
    """
    A streamfield for aesthetically pleasing, 
    automatically generated lists of links 
    with an icon.
    """
    icon = CharBlock(help_text="Add a Font Awesome icon name here")
    starting_page = PageChooserBlock()

    def get_context(self, value): 
        context = super(IconAutoListBlock, self).get_context(value) 
        url_path = value['starting_page'].url_path
    
        d = []
        for child in sorted(list(Page.objects.get(url_path=url_path).get_children().in_menu().live().specific()), key=lambda p: (p.sort_order, p.title)):
            c = {
                'title': child.title,
                'url': child.url,
                'children': []
            }
            for grandchild in sorted(list(child.get_children().in_menu().live().specific()), key=lambda p: (p.sort_order, p.title)):
                c['children'].append({
                    'title': grandchild.title,
                    'url': grandchild.url
                })
            d.append(c)
        context['descendants'] = d
        return context 

    class Meta:
        icon = 'folder'
        template = 'intranettocs/blocks/icon_automatic_directory_list.html'


class IconListCluster(StreamBlock):
    """
    Standard default streamfield options to be shared
    across content types.
    """
    list_block = IconListBlock()
    automatic_directory_list_block = IconAutoListBlock()


