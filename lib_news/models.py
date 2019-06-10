from base.models import DefaultBodyFields, PublicBasePage
from django.db import models
from modelcluster.fields import ParentalKey
from rest_framework import serializers
from wagtail.admin.edit_handlers import (
    FieldPanel, InlinePanel, MultiFieldPanel, ObjectList, StreamFieldPanel,
    TabbedInterface
)
from wagtail.api import APIField
from wagtail.core.fields import StreamField
from wagtail.core.models import Orderable, Page
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.snippets.models import register_snippet


@register_snippet
class PublicNewsCategories(models.Model, index.Indexed):
    text = models.CharField(max_length=255, blank=False)

    panels = [
        FieldPanel('text'),
    ]

    def __str__(self):
        return self.text

    search_fields = [
        index.SearchField('text', partial_match=True),
    ]

    class Meta:
        verbose_name = "Public News Category"
        verbose_name_plural = "Public News Categories"


class LibNewsPageCategories(Orderable, models.Model):
    page = ParentalKey(
        'lib_news.LibNewsPage',
        on_delete=models.CASCADE,
        related_name='lib_news_categories'
    )
    category = models.ForeignKey(
        'lib_news.PublicNewsCategories',
        on_delete=models.CASCADE,
        related_name='+'
    )

    panels = [
        SnippetChooserPanel('category'),
    ]

    def __str__(self):
        return self.page.title + " -> " + self.category.text


class LibNewsIndexPage(PublicBasePage):

    subpage_types = ['lib_news.LibNewsPage']

    content_panels = Page.content_panels + PublicBasePage.content_panels

    widget_content_panels = [
        MultiFieldPanel(
            [
                ImageChooserPanel('banner_image'),
                FieldPanel('banner_title'),
            ],
            heading='Banner'
        ),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading='Content'),
            ObjectList(PublicBasePage.promote_panels, heading='Promote'),
            ObjectList(
                Page.settings_panels, heading='Settings', classname="settings"
            ),
            ObjectList(widget_content_panels, heading='Widgets'),
        ]
    )

    search_fields = PublicBasePage.search_fields


class LibNewsPage(PublicBasePage):

    body = StreamField(DefaultBodyFields())

    def get_categories(self):
        """
        Get a list of categories assigned to the news page.

        Returns:
            list of strings
        """
        return [
            str(PublicNewsCategories.objects.get(id=cat['category_id']))
            for cat in self.lib_news_categories.values()
        ]

    subpage_types = []

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
        InlinePanel('lib_news_categories', label='Categories'),
    ] + PublicBasePage.content_panels

    search_fields = PublicBasePage.search_fields + [
        index.SearchField('body', partial_match=True),
    ]

    api_fields = [
        APIField(
            'categories',
            serializer=serializers.ListField(source='get_categories')
        ),
    ]
