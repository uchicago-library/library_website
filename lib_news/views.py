from requests import get
from django.contrib.syndication.views import Feed
from lib_news.models import LibNewsPage, LibNewsIndexPage, LibNewsPageCategories, PublicNewsCategories
from django.http.response import StreamingHttpResponse
from wagtailcache.cache import cache_page
from django.utils.decorators import method_decorator
from datetime import date, timedelta
from django.utils.text import slugify

from library_website.settings import STATIC_NEWS_FEED


@cache_page
def ltdrfr(request):
    """
    Let the Django Rest Framework Rest.
    """
    response = StreamingHttpResponse(content=open(STATIC_NEWS_FEED, 'rb'))
    return response


@method_decorator(cache_page, name='items')
class RSSFeeds(Feed):
    def get_object(self, request, slug):
        """Part of the Django syndication API; in this case, returns
        the category of the feed.
        """
        category = LibNewsIndexPage.get_cat_from_slug_static(slug)
        return PublicNewsCategories.objects.filter(text=category).first()
    
    def title(self, obj):
        """Title for the whole feed.
        """
        return "RSS Feed for the %s News Category" % obj.text
    
    link = "/rss/"
    
    description = 'News Stories, UChicago Library!'
    
    def items(self, obj):
        """Generates the list of items in the feed."""
        def has_category(cat):
            def partial_application(page):
                return cat in page.get_categories()
            return partial_application

        c = obj.text
        window = date.today() - timedelta(weeks=78)
        stories = (LibNewsPage
                   .objects
                   .filter(published_at__gt=window)
                   .order_by('-published_at')
        )
        
        return filter(has_category(c), stories)
    
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
