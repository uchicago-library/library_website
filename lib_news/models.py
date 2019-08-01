import bleach
from base.models import (
    ContactPersonBlock, DefaultBodyFields, PublicBasePage, RelatedExhibitBlock
)
from django.db import models
from django.template.defaultfilters import slugify
from django.template.response import TemplateResponse
from django.utils import timezone
from lib_collections.models import get_current_exhibits
from library_website.settings import (
    NEWS_FEED_DEFAULT_VISIBLE, NEWS_FEED_INCREMENT_BY
)
from modelcluster.fields import ParentalKey
from rest_framework import serializers
from wagtail.admin.edit_handlers import (
    FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel, ObjectList,
    PageChooserPanel, StreamFieldPanel, TabbedInterface
)
from wagtail.api import APIField
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Orderable, Page
from wagtail.images.api.fields import ImageRenditionField
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.snippets.models import register_snippet

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


class LibNewsIndexPage(RoutablePageMixin, PublicBasePage):

    def __init__(self, *args, **kwargs):
        super(PublicBasePage, self).__init__(*args, **kwargs)
        self.is_unrouted = True
        self.news_feed_api = '/api/v2/pages/?format=json&treat_as_webpage=false&limit=500&order=-published_at&type=lib_news.LibNewsPage&fields=*'

    contacts = StreamField(ContactPersonBlock(required=False), default=[])

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

    @route(r'^search/$')
    def search(self, request, *args, **kwargs):
        """
        Search results view.
        """
        self.search_query = request.GET.get('query', '')
        self.news_feed_api = '/api/v2/pages/?search=%s&format=json&treat_as_webpage=false&limit=500&type=lib_news.LibNewsPage&fields=*' % self.search_query
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
        context = super(LibNewsIndexPage, self).get_context(request)
        context['categories'] = self.get_alpha_cats()
        context['category_url_base'] = self.base_url + 'category/'
        context['search_url_base'] = self.base_url + 'search/'
        context['news_feed_api'] = self.news_feed_api
        context['feature'] = get_first_feature_story()
        context['current_exhibits'] = get_current_exhibits()
        context['display_current_web_exhibits'
                ] = self.display_current_web_exhibits
        context['contacts'] = self.contacts
        context['content_div_css'] = 'container-fluid main-container'
        context['breadcrumb_div_css'] = 'hidden'
        context['right_sidebar_classes'] = 'coll-rightside'
        context['fallback_image'] = self.fallback_image
        context['default_visible'] = NEWS_FEED_DEFAULT_VISIBLE
        context['increment_by'] = NEWS_FEED_INCREMENT_BY
        return context


class LibNewsPage(PublicBasePage):

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
    by_staff = models.ForeignKey(
        'staff.StaffPage',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL
    )
    by_unit = models.ForeignKey(
        'units.UnitPage',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL
    )
    by_text_box = models.CharField(max_length=200, blank=True)
    published_at = models.DateTimeField(default=timezone.now)
    library_kiosk = models.BooleanField(default=False)
    law_kiosk = models.BooleanField(default=False)
    crerar_kiosk = models.BooleanField(default=False)
    scrc_kiosk = models.BooleanField(default=False)
    treat_as_webpage = models.BooleanField(
        default=False,
        help_text='Functionally converts this page to a standard page. \
        If checked, the page will not appear in news feeds'
    )

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

    def get_first_feature_story_id(self):
        """
        Get id of the first feature story.

        Returns:
            int
        """
        ff = get_first_feature_story()
        if ff:
            return ff.id
        else:
            return None

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
        return LibNewsPage.objects.order_by(field).exclude(
            thumbnail=None
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
                PageChooserPanel('by_staff'),
                PageChooserPanel('by_unit'),
                FieldPanel('by_text_box'),
            ],
            heading='Author'
        ),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel('law_kiosk', classname=ROW_CLASS),
                        FieldPanel('crerar_kiosk', classname=ROW_CLASS),
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
        index.SearchField('by_text_box'),
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
        APIField(
            'first_feature_id',
            serializer=serializers.IntegerField(
                source='get_first_feature_story_id'
            )
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
        context['breadcrumb_div_css'] = parent_context['breadcrumb_div_css']
        context['right_sidebar_classes'
                ] = parent_context['right_sidebar_classes']
        return context
