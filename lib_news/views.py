from datetime import date, timedelta

from django.contrib.syndication.views import Feed
from django.http.response import StreamingHttpResponse
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from requests import get
from wagtailcache.cache import cache_page

from lib_news.models import (
    LibNewsIndexPage, LibNewsPage, LibNewsPageCategories, PublicNewsCategories
)
from library_website.settings import STATIC_NEWS_FEED


@cache_page
def ltdrfr(request):
    """
    Let the Django Rest Framework Rest.
    """
    response = StreamingHttpResponse(content=open(STATIC_NEWS_FEED, 'rb'))
    return response


class RSSFeeds(Feed):

    def get_object(self, request, slug):
        """Part of the Django syndication API; in this case, returns
        the category of the feed.
        """
        try:
            category = LibNewsIndexPage.get_cat_from_slug_static(slug)
            return PublicNewsCategories.objects.filter(text=category).first()
        except KeyError:
            return None

    def title(self, obj):
        """Title for the whole feed.
        """
        if obj:
            return "RSS Feed for the %s News Category" % obj.text
        else:
            return "RSS Feed for Library News"

    link = "/rss/"

    description = 'News Stories: The University of Chicago Library'

    def items(self, obj):
        """Generates the list of items in the feed."""

        def has_category(cat):

            def partial_application(page):
                return cat in page.get_categories()

            return partial_application

        stories = LibNewsPage.objects.order_by('-published_at')

        if obj:
            c = obj.text
            return list(filter(has_category(c), stories))[:20]
        else:
            return stories[:20]

    def item_title(self, item):
        """Title for each feed story."""
        return item.title

    def item_description(self, item):
        """Content of each story."""
        return item.short_description

    def item_pubdate(self, item):
        """Publication date of each story."""
        return item.published_at

    def item_link(self, item):
        """Link to each story."""
        return item.url
