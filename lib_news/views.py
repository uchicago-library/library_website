from django.http.response import StreamingHttpResponse
from wagtailcache.cache import cache_page

from library_website.settings import STATIC_NEWS_FEED


@cache_page
def ltdrfr(request):
    """
    Let the Django Rest Framework Rest.
    """
    response = StreamingHttpResponse(content=open(STATIC_NEWS_FEED, 'rb'))
    return response
