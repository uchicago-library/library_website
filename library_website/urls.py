from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic.base import RedirectView
from django.urls import path
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from base.views import chat_status, external_include, json_events, json_hours
from events.views import events as events_view
from lib_collections.views import collections as collection_view
from lib_collections.views import citation_display as citation_display
from lib_news.views import ltdrfr
from lib_news.views import RSSFeeds
from public.views import navigation as navigation_view
from public.views import spaces as spaces_view
from public.views import switchboard
from results.views import results as results_view
from search.views import loop_search as search_view, ebooks_search
from staff.views import staff, staff_api
from units.views import units as unit_view

from .api import api_router

urlpatterns = [
    url(r'^django-admin/', admin.site.urls),
    url(r'^shib/', include('shibboleth.urls', namespace='shibboleth')),
    url(r'^admin/', include(wagtailadmin_urls)),
    url(r'^documents/', include(wagtaildocs_urls)),
    url(r'^navigation-elements/', navigation_view, name='navigation-view'),
    url(r'^json-hours/', json_hours, name='json-hours'),
    url(r'^json-events/', json_events, name='json-events'),
    url(r'^external-include/', external_include, name='external-include'),
    url(r'^chat-status/', chat_status, name='chat-status'),
    url(r'^results/$', results_view, name='results'),
    url(r'^ltdrfr/$', ltdrfr, name='ltdrfr'),
    url(r'^loop-search/$', search_view, name='search'),
    url(r'^ebooks-search/$', ebooks_search, name='ebooks'),
    url(r'^api/v2/', api_router.urls),
    url('^inventory\.xml$', sitemap),
    url(r'^spaces/$', spaces_view, name='spaces'),
    url(r'^staff/$', staff, name='staff'),
    url(r'^staff_api/$', staff_api, name='staff_api'),
    url(r'^about/directory/$', unit_view, name='unit'),
    url(r'^switchboard/$', switchboard, name='switchboard'),
    url(
        r'^about/directory/staff/$',
        RedirectView.as_view(url='/about/directory/?view=staff')
    ),
    url(r'^about/news-events/events/$', events_view, name='events'),
    url(r'^collex/$', collection_view, name='collection'),
    url(r'^citation_display$', citation_display, name='citation_display'),
    url(r'^collex/collections/$', RedirectView.as_view(url='/collex/')),
    url(
        r'^collex/exhibits/$',
        RedirectView.as_view(url='/collex/?view=exhibits')
    ),
    url(r'^workflowautomator/', include('workflowautomator.urls')),
    url(r'rss/(?P<slug>[-\w]+)/$', RSSFeeds()),
    url(r'', include(wagtail_urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Prepend the shibboleth logout url if the application
# is configured for shibboleth
# if settings.SHIBBOLETH_LOGOUT_URL:
#    urlpatterns.insert(0, url(r'^admin/logout/$', RedirectView.as_view(url='/shib/logout/?target=%s', permanent=True), name='logout'), )

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
