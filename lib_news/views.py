from requests import get
from django.contrib.syndication.views import Feed
from lib_news.models import LibNewsPage, LibNewsPageCategories, PublicNewsCategories
from django.http.response import StreamingHttpResponse
from wagtailcache.cache import cache_page
from django.utils.text import slugify

from library_website.settings import STATIC_NEWS_FEED
# from django.views.generic.base import TemplateView


@cache_page
def ltdrfr(request):
    """
    Let the Django Rest Framework Rest.
    """
    response = StreamingHttpResponse(content=open(STATIC_NEWS_FEED, 'rb'))
    return response


class RSSFeeds(Feed):
    title = 'News Stories RSS Feed'
    link = 'rss/' 
    description = 'News Stories, UChicago Library!'
   
    def get_object(self, request, catid):
        ids = [ str(x.id) for x in list(PublicNewsCategories.objects.all()) ]
        cats = [ x.text for x in list(PublicNewsCategories.objects.all()) ]
        lookup_table = dict(zip(ids,cats))
        cid = lookup_table[catid]
        
        return PublicNewsCategories.objects.filter(text=cid).first()
        # class RContext:
        #     def __init__(self, cat):
        #         self.category = cat
        # return RContext(category)

    def always_true(x):
        return True

    def correct_category(cat):
        def _correct_category(page):
            # return cat in [ slugify(c) for c in page.get_categories() ]
            return cat in page.get_categories()
        return _correct_category
    
    def items(self, obj):
        correct = RSSFeeds.correct_category(obj.text)
        return filter(correct, LibNewsPage.objects.all())

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.short_description
    
    def item_link(self, item):
        return item.url
