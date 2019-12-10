import json
from urllib.request import URLError, urlopen

from django.contrib.syndication.views import Feed
from django.http import HttpResponse

import bleach
from django.core.cache import cache, caches
from django.db import models
from django.template.defaultfilters import slugify
from django.template.response import TemplateResponse
from django.utils import timezone
from modelcluster.fields import ParentalKey
from rest_framework import serializers
from wagtail.admin.edit_handlers import (
    FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel, ObjectList,
    PageChooserPanel, StreamFieldPanel, TabbedInterface
)
from wagtail.api import APIField
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.core.blocks import PageChooserBlock
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Orderable, Page
from wagtail.core.signals import page_published, page_unpublished
from wagtail.images.api.fields import ImageRenditionField
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.snippets.models import register_snippet
from wagtailcache.cache import clear_cache

from base.models import (
    ContactPersonBlock, DefaultBodyFields, PublicBasePage, RelatedExhibitBlock
)
from lib_collections.models import get_current_exhibits
from library_website.settings import (
    DRF_NEWS_FEED, LIBRA_ID, NEWS_CACHE_TTL, NEWS_FEED_DEFAULT_VISIBLE,
    NEWS_FEED_INCREMENT_BY, STATIC_NEWS_FEED
)

from .utils import get_first_feature_story


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


@register_snippet
class PublicNewsAuthors(models.Model, index.Indexed):
    author_name = models.CharField(max_length=255, blank=False)
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL
    )
    link_external = models.URLField(max_length=400, null=True, blank=True)

    panels = [
        FieldPanel('author_name'),
        MultiFieldPanel(
            [
                PageChooserPanel('link_page'),
                FieldPanel('link_external'),
            ],
            heading='Author Link'
        )
    ]

    def __str__(self):
        return self.author_name

    search_fields = [
        index.SearchField('name', partial_match=True),
    ]

    class Meta:
        verbose_name = "Public News Author"
        verbose_name_plural = "Public News Authors"


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
        return self.category.text


class LibNewsIndexPage(RoutablePageMixin, PublicBasePage):

    def __init__(self, *args, **kwargs):
        super(PublicBasePage, self).__init__(*args, **kwargs)
        self.is_unrouted = True
        self.news_feed_api = '/static/lib_news/files/lib-news.json'

    contacts = StreamField(ContactPersonBlock(required=False), default=[])

    navigation = StreamField(
        [
            (
                'navigation',
                PageChooserBlock(
                    required=False, page_type=['lib_news.LibNewsPage']
                )
            ),
        ],
        default=[],
        null=True,
        blank=True,
    )

    fallback_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text='Image to be used in browse display \
        when no thumbnail is provided',
        related_name='+'
    )

    subpage_types = ['lib_news.LibNewsPage']

    content_panels = Page.content_panels + [
        ImageChooserPanel('fallback_image'),
        StreamFieldPanel('navigation'),
    ] + PublicBasePage.content_panels

    widget_content_panels = [
        MultiFieldPanel(
            [
                ImageChooserPanel('banner_image'),
                FieldPanel('banner_title'),
            ],
            heading='Banner'
        ),
        MultiFieldPanel(
            [
                FieldPanel('events_feed_url'),
            ], heading='Workshops and Events'
        ),
        MultiFieldPanel(
            [
                FieldPanel('display_current_web_exhibits'),
            ],
            heading='Current Web Exhibits'
        ),
        StreamFieldPanel('contacts'),
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

    search_fields = PublicBasePage.search_fields + [
        index.SearchField('contacts'),
    ]

    @property
    def has_right_sidebar(self):
        """
        Determine if a right sidebar should
        be displayed in the template.

        Returns:
            boolean
        """
        return True


    # @route('binky')
    # def binky_view2(self, request, *args, **kwargs):
    #     """
    #     Route to templete for browsing stories by
    #     category.
    #     """
    #     return HttpResponse("Francis Ford Coppola")
    
    # @route('binky')
    # def binky_view(self, request, *args, **kwargs):
    #     """
    #     Route to templete for browsing stories by
    #     category.
    #     """
    #     return HttpResponse("Binky")

       
    @route(r'^category/(?P<slug>[-\w]+)/$')
    def category(self, request, *args, **kwargs):
        """
        Route to templete for browsing stories by
        category.
        """
        self.is_unrouted = False
        try:
            slug = request.path.split('/')[-2]
            self.category = self.get_cat_from_slug(slug)
        except (KeyError):
            self.category = ''
        return TemplateResponse(
            request, self.get_template(request), self.get_context(request)
        )

    # @route(r'^category/(?P<slug>[-\w]+)/rss/$')
    # def category_rss(self, request, *args, **kwargs):
    #     """
    #     Route to rss feed for a category.
    #     """
    #     # output = lib_news.views.RSSFeeds()
    #     category = kwargs['slug']
    #     return HttpResponse(category)

    @route(r'^search/$')
    def search(self, request, *args, **kwargs):
        """
        Search results view.
        """
        self.search_query = request.GET.get('query', '')
        self.news_feed_api = '/api/v2/pages/?search={}&format=json&type=lib_news.LibNewsPage&fields=*'.format(
            self.search_query
        )
        self.is_unrouted = False
        return TemplateResponse(
            request, self.get_template(request), self.get_context(request)
        )

    def get_alpha_cats(self):
        """
        Get a list of categories sorted alphabetically.

        Returns:
            list of strings
        """
        return list(
            s[0] for s in
            PublicNewsCategories.objects.order_by('text').values_list('text')
        )

    def get_first_feature_story_id(self):
        """
        Get id of the first feature story.

        Returns:
            int
        """
        ff = get_first_feature_story()
        if ff:
            return str(ff.id)
        else:
            return ''

    def get_cat_from_slug(self, slug):
        """
        Creates a lookup table of category names by slug
        and returns a match for the given slug.
        """
        categories = self.get_alpha_cats()
        lookup_table = {}
        for cat in categories:
            lookup_table[slugify(cat)] = cat
        return lookup_table[slug]

    @property
    def base_url(self):
        return self.get_url_parts()[-1]

    def get_context(self, request):
        """
        Override the page object's get context method.
        """
        try:
            libra = Page.objects.get(id=LIBRA_ID)
        except (Page.DoesNotExist):
            libra = None
        context = super(LibNewsIndexPage, self).get_context(request)
        context['categories'] = self.get_alpha_cats()
        context['category_url_base'] = self.base_url + 'category/'
        context['search_url_base'] = self.base_url + 'search/'
        context['news_feed_api'] = self.news_feed_api
        context['feature'] = get_first_feature_story()
        context['feature_id'] = self.get_first_feature_story_id()
        context['current_exhibits'] = get_current_exhibits()
        context['display_current_web_exhibits'
                ] = self.display_current_web_exhibits
        context['contacts'] = self.contacts
        context['content_div_css'] = 'container-fluid main-container'
        context['right_sidebar_classes'] = 'coll-rightside'
        context['fallback_image'] = self.fallback_image
        context['default_visible'] = NEWS_FEED_DEFAULT_VISIBLE
        context['increment_by'] = NEWS_FEED_INCREMENT_BY
        context['nav'] = self.navigation
        context['libra'] = libra
        return context


class LibNewsPage(PublicBasePage):

    def __init__(self, *args, **kwargs):
        super(LibNewsPage, self).__init__(*args, **kwargs)
        self.news_pages = LibNewsPage.objects.live(
        ).prefetch_related('lib_news_categories')

    body = StreamField(DefaultBodyFields())
    thumbnail = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    alt_text = models.CharField(max_length=100, blank=True)
    is_feature_story = models.BooleanField(default=False)
    excerpt = RichTextField(blank=True)
    related_exhibits = StreamField(
        RelatedExhibitBlock(required=False), default=[]
    )
    by_staff_or_unit = models.ForeignKey(
        'lib_news.PublicNewsAuthors',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    custom_author_byline = models.CharField(max_length=360, blank=True)
    published_at = models.DateTimeField(default=timezone.now)
    library_kiosk = models.BooleanField(default=False)
    law_kiosk = models.BooleanField(default=False)
    sciences_kiosk = models.BooleanField(default=False)
    scrc_kiosk = models.BooleanField(default=False)
    treat_as_webpage = models.BooleanField(
        default=False,
        help_text='Functionally converts this page to a standard page. \
        If checked, the page will not appear in news feeds'
    )
    exhibit_story_hours_override = RichTextField(blank=True)

    def get_categories(self):
        """
        Get a list of categories assigned to the news page. Categories
        are cached in redis as a dictionary where the keys are page IDs
        and the values are lists of string category names.

        Returns:
            list of strings
        """
        try:
            dcache = caches['default']
            cdict = {}
            pid = self.id
            if 'news_cats' not in dcache:
                dcache.set('news_cats', cdict, NEWS_CACHE_TTL)
            if 'news_cats' in dcache:
                cdict = dcache.get('news_cats')
                if pid in cdict:
                    cats = cdict[pid]
                else:
                    cats = [
                        str(cat)
                        for cat in self.lib_news_categories.get_object_list()
                    ]
                    cdict[pid] = cats
                    dcache.set('news_cats', cdict, NEWS_CACHE_TTL)
            return cats
        # This is a FakeQuerySet and we are probably in preview mode.
        # To handle this, we won't show any categories.
        except (AttributeError):
            return [
                'Can\'t load categories in PREVIEW',
                'Check categories on the LIVE page'
            ]

    @property
    def short_description(self):
        if self.excerpt:
            retval = self.excerpt
        else:
            retval = self.body
        # return retval
        return bleach.clean(
            retval,
            tags=['a', 'b', 'i'],
            attributes={'a': ['href', 'rel', 'data', 'id', 'linktype']},
            strip=True,
            strip_comments=True,
        )

    @property
    def has_right_sidebar(self):
        """
        Determine if a right sidebar should
        be displayed in the template.

        Returns:
            boolean
        """
        return True

    def get_recent_stories(self, n, field):
        """
        Gets the n most rescent stories sorted by the
        field name passed.

        Args:
            n: int, number of stories to return

            field: string, field to be passed to a
            Django QuerySet filter, e.g. '-published_at'.
        """
        return self.news_pages.order_by(field).exclude(thumbnail=None
                                                       ).exclude(id=self.id)[:n]

    subpage_types = []

    ROW_CLASS = 'col4'

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                ImageChooserPanel('thumbnail'),
                FieldPanel('alt_text'),
            ],
            heading='Thumbnail',
        ),
        FieldPanel('is_feature_story'),
        FieldPanel('excerpt'),
        StreamFieldPanel('body'),
        InlinePanel('lib_news_categories', label='Categories'),
        FieldPanel('published_at'),
        MultiFieldPanel(
            [
                SnippetChooserPanel('by_staff_or_unit'),
                FieldPanel('custom_author_byline'),
            ],
            heading='Author'
        ),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel('law_kiosk', classname=ROW_CLASS),
                        FieldPanel('sciences_kiosk', classname=ROW_CLASS),
                        FieldPanel('scrc_kiosk', classname=ROW_CLASS),
                        FieldPanel('library_kiosk', classname=ROW_CLASS),
                    ]
                )
            ],
            heading='Publish to'
        ),
    ] + PublicBasePage.content_panels

    widget_content_panels = [
        StreamFieldPanel('related_exhibits'),
        FieldPanel('treat_as_webpage'),
        MultiFieldPanel(
            [
                FieldPanel('quicklinks_title'),
                FieldPanel('quicklinks'),
                FieldPanel('view_more_link_label'),
                FieldPanel('view_more_link'),
                FieldPanel('change_to_callout'),
            ],
            heading='Rich Text'
        ),
        FieldPanel('exhibit_story_hours_override'),
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

    search_fields = PublicBasePage.search_fields + [
        index.SearchField('body', partial_match=True),
        index.SearchField('alt_text'),
        index.SearchField('excerpt'),
        index.SearchField('related_exhibits'),
        index.SearchField('custom_author_byline'),
        index.SearchField('published_at'),
    ]

    api_fields = [
        APIField('is_feature_story'),
        APIField(
            'categories',
            serializer=serializers.ListField(source='get_categories')
        ),
        APIField(
            'thumbnail', serializer=ImageRenditionField('fill-500x425-c50')
        ),
        APIField(
            'thumbnail_alt_text',
            serializer=serializers.CharField(source='alt_text')
        ),
        APIField('published_at'),
        APIField('treat_as_webpage'),
    ]

    def get_context(self, request):
        """
        Override the page object's get context method.
        """
        context = super(LibNewsPage, self).get_context(request)
        parent = self.get_parent_of_type('lib news index page')
        parent_context = parent.get_context(request)
        self.events_feed_url = parent.events_feed_url
        context['categories'] = parent.get_alpha_cats()
        context['tagged'] = self.get_categories()
        context['category_url_base'] = parent_context['category_url_base']
        context['search_url_base'] = parent_context['search_url_base']
        context['contacts'] = parent_context['contacts']
        context['display_current_web_exhibits'
                ] = parent_context['display_current_web_exhibits']
        context['current_exhibits'] = parent_context['current_exhibits']
        context['events_feed'] = parent_context['events_feed']
        context['recent_stories'] = self.get_recent_stories(3, '-published_at')
        context['content_div_css'] = parent_context['content_div_css']
        context['right_sidebar_classes'
                ] = parent_context['right_sidebar_classes']
        context['nav'] = parent_context['nav']
        context['libra'] = parent_context['libra']
        return context


def build_news_feed(sender, instance, **kwargs):
    """
    Build a static version of the news feed when a LibNewsPage is
    published or unpublished. Query the Django Rest Framework
    (Wagtail v2 API) and save the results to a static JSON file
    in the static files directory.

    Args:
        sender: LibNewsPage class

        instance: LibNewsPage instance

    Returns:
        None but writes a file to the static directory
    """
    clear_cache()
    cache.delete('news_cats')
    drf_url = instance.get_site().root_url + DRF_NEWS_FEED
    try:
        serialized_data = urlopen(drf_url).read()
        data = json.loads(serialized_data)
        with open(STATIC_NEWS_FEED, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=None)
    except(URLError):
        # We are running unit tests
        return None
    
page_published.connect(build_news_feed, sender=LibNewsPage)
page_unpublished.connect(build_news_feed, sender=LibNewsPage)
