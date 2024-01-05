from base.views import chat_status, external_include, json_events, json_hours
from django.conf import settings
from django.urls import include, re_path
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic.base import RedirectView
from events.views import events as events_view
from item_servlet.views import item_servlet
from lib_collections.views import citation_display as citation_display
from lib_collections.views import collections as collection_view
from lib_news.views import RSSFeeds, ltdrfr
from public.views import navigation as navigation_view
from public.views import spaces as spaces_view
from public.views import switchboard
from results.views import results as results_view
from search.views import ebooks_search
from search.views import loop_search as search_view
from staff.views import staff, staff_api
from units.views import units as unit_view
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.documents import urls as wagtaildocs_urls
from intranethome.views import mail_aliases_view

from .api import api_router

urlpatterns = [
    re_path(r'^django-admin/', admin.site.urls),
    re_path(r'^shib/', include('shibboleth.urls', namespace='shibboleth')),
    re_path(r'^admin/', include(wagtailadmin_urls)),
    re_path(r'^documents/', include(wagtaildocs_urls)),
    re_path(r'^navigation-elements/', navigation_view, name='navigation-view'),
    re_path(r'^json-hours/', json_hours, name='json-hours'),
    re_path(r'^json-events/', json_events, name='json-events'),
    re_path(r'^external-include/', external_include, name='external-include'),
    re_path(r'^chat-status/', chat_status, name='chat-status'),
    re_path(r'^item-servlet/', item_servlet, name='item-servlet'),
    re_path(r'^results/$', results_view, name='results'),
    re_path(r'^ltdrfr/$', ltdrfr, name='ltdrfr'),
    re_path(r'^loop-search/$', search_view, name='search'),
    re_path(r'^ebooks-search/$', ebooks_search, name='ebooks'),
    re_path(r'^api/v2/', api_router.urls),
    re_path('^inventory\.xml$', sitemap),
    re_path(r'^spaces/$', spaces_view, name='spaces'),
    re_path(r'^staff/$', staff, name='staff'),
    re_path(r'^staff_api/$', staff_api, name='staff_api'),
    re_path(r'^about/directory/$', unit_view, name='unit'),
    re_path(r'^switchboard/$', switchboard, name='switchboard'),
    re_path(
        r'^about/directory/staff/$',
        RedirectView.as_view(url='/about/directory/?view=staff')
    ),
    re_path(r'^about/news-events/events/$', events_view, name='events'),
    re_path(r'^collex/$', collection_view, name='collection'),
    re_path(r'^mailaliases/', mail_aliases_view, name='mail_aliases'),
    re_path(r'^citation_display$', citation_display, name='citation_display'),
    re_path(r'^collex/collections/$', RedirectView.as_view(url='/collex/')),
    # re_path(
    #    r'^collex/exhibits/$',
    #    RedirectView.as_view(url='/collex/?view=exhibits')
    # ),
    re_path(r'^workflowautomator/', include('workflowautomator.urls')),
    re_path(r'rss/(?P<slug>[-\w]+)/$', RSSFeeds()),
    # re_path(r'', include(wagtail_urls)),
] + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)

# Prepend the shibboleth logout url if the application
# is configured for shibboleth
# if settings.SHIBBOLETH_LOGOUT_URL:
#    urlpatterns.insert(0, re_path(r'^admin/logout/$', RedirectView.as_view(url='/shib/logout/?target=%s', permanent=True), name='logout'), )

# Multi-lingual support
urlpatterns += i18n_patterns(
    re_path(
        r'^collex/exhibits/$',
        RedirectView.as_view(url='/collex/?view=exhibits')
    ),
    re_path(r'^collex/$', collection_view, name='collection'),
    re_path(r'^collex/collections/$', RedirectView.as_view(url='/collex/')),
    re_path(r'', include(wagtail_urls)),
    prefix_default_language=False,
)

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

handler404 = 'library_website.views.library_404_view'
