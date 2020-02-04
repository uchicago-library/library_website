from django.contrib.syndication.views import Feed
from django.http.response import StreamingHttpResponse
from wagtailcache.cache import cache_page

from lib_news.models import LibNewsIndexPage, LibNewsPage, PublicNewsCategories
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
        """
        Part of the Django syndication API.

        Args: RSS Feed object, HTTP request, and a slug passed in from
        urls.py

        Returns: a singleton QuerySet consisting of the news category
        corresponding to the slug in the URL
        """
        try:
            category = LibNewsIndexPage.get_cat_from_slug_static(slug)
            return PublicNewsCategories.objects.filter(text=category).first()
        except KeyError:
            return None

    def title(self, obj):
        """
        Defines the title of the entire feed.

        Args: RSS Feed object, singleton category QuerySet

        Returns: a string corresponding to the title of the feed
        """
        if obj:
            return "RSS Feed for the %s News Category" % obj.text
        else:
            return "RSS Feed for Library News"

    link = "/rss/"

    description = "News Stories: The University of Chicago Library"

    def items(self, obj):
        """
        Generates the list of items in the feed.  Restricts to news
        category if there is one in the URL; otherwise constructs a
        feed of all library news stories.

        Args: RSS Feed object, singleton category QuerySet

        Returns: list of Lib News Page objects
        """

        def has_category(cat):
            """
            Predicate true just in case page belongs to input category.
            Curried for use in the filter below.

            Args: (string) name of category, Lib News Page

            Returns: boolean
            """

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
        """
        Determines the title for each feed story.

        Args: RSS Feed object, RSS item object

        Returns: (string) title of the item
        """
        return item.title

    def item_description(self, item):
        """
        Determines the content of each story.

        Args: RSS Feed object, RSS item object

        Returns: (string) description of the item
        """
        return item.short_description

    def item_pubdate(self, item):
        """
        Determines the publication date of each story.

        Args: RSS Feed object, RSS item object

        Returns: (datetime) publication date of the item
        """
        return item.published_at

    def item_link(self, item):
        """
        Determines the URL for each story.

        Args: RSS Feed objet, RSS item object

        Returns: (string) URL for the News page for the item
        """
        return item.url
