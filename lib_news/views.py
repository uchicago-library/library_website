from requests import get
from django.contrib.syndication.views import Feed
from lib_news.models import LibNewsPage, LibNewsIndexPage, LibNewsPageCategories, PublicNewsCategories
from django.http.response import StreamingHttpResponse
from wagtailcache.cache import cache_page
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


class RSSFeeds(Feed):
   
    def get_object(self, request, slug):
        category = LibNewsIndexPage.get_cat_from_slug_static(slug)
        return PublicNewsCategories.objects.filter(text=category).first()
        
    def title(self, obj):
        return "RSS Feed for the %s News Category" % obj.text
            
    link = "/rss/"
    
    description = 'News Stories, UChicago Library!'
    
    def items(self, obj):
        def has_category(cat):
            def partial_application(page):
                return cat in page.get_categories()
            return partial_application
        c = obj.text
        a_year = date.today() - timedelta(days=365)
        return filter(has_category(c), LibNewsPage.objects.filter(published_at__gt=a_year).order_by('-published_at'))

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.short_description

    def item_pubdate(self, item):
        return item.published_at
    
    def item_link(self, item):
        return item.url
