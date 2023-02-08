from itertools import chain

from ask_a_librarian.utils import (get_chat_status, get_chat_status_css,
                                   get_unit_chat_link)
from base.utils import get_hours_and_location
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import render
from library_website.settings import PUBLIC_HOMEPAGE, RESTRICTED
from public.models import StandardPage
from searchable_content.models import (LibGuidesAssetsSearchableContent,
                                       LibGuidesSearchableContent)
from units.models import UnitIndexPage
from wagtail.contrib.search_promotions.models import SearchPromotion
from wagtail.models import Page, Site
from wagtail.search.backends import get_search_backend
from wagtail.search.models import Query


def results(request):
    search_query = request.GET.get('query', None)
    page = request.GET.get('page', 1)

    # Search
    if search_query:
        homepage = Site.objects.get(site_name="Public").root_page
        unit_index_page = UnitIndexPage.objects.first()
        restricted = StandardPage.objects.live().get(id=RESTRICTED)
        search_results1 = Page.objects.live().descendant_of(
            homepage).not_descendant_of(
                unit_index_page, True).not_descendant_of(
                    restricted, True).search(
                        search_query, operator="and").annotate_score('score')
        search_backend = get_search_backend()

        search_results2 = search_backend.search(
            search_query,
            LibGuidesSearchableContent.objects.all(),
            operator="and").annotate_score('score')
        r = 0
        while r < len(search_results2):
            search_results2[r].score = search_results2[r].score * 1.5
            r += 1

        r = 0
        while r < len(search_results2):
            search_results2[r].searchable_content = 'guides'
            r += 1

        search_results3 = search_backend.search(
            search_query,
            LibGuidesAssetsSearchableContent.objects.all(),
            operator="and").annotate_score('score')
        r = 0
        while r < len(search_results3):
            search_results3[r].searchable_content = 'assets'
            r += 1

        search_results = list(
            chain(search_results1, search_results2, search_results3))
        try:
            search_results.sort(key=lambda r: r.score, reverse=True)
        except (TypeError):
            pass

        query = Query.get(search_query)

        # Record hit
        query.add_hit()

        # Get search picks
        search_picks = query.editors_picks.all()
    else:
        search_results = Page.objects.none()
        search_picks = SearchPromotion.objects.none()

    # Pagination
    paginator = Paginator(search_results, 10)
    try:
        search_results = paginator.page(page)
    except PageNotAnInteger:
        search_results = paginator.page(1)
    except EmptyPage:
        search_results = paginator.page(paginator.num_pages)

    # Page context variables for templates
    home_page = StandardPage.objects.live().get(id=PUBLIC_HOMEPAGE)
    location_and_hours = get_hours_and_location(home_page)
    location = str(location_and_hours['page_location'])
    unit = location_and_hours['page_unit']

    return render(
        request, 'results/results.html', {
            'breadcrumb_div_css': 'col-md-12 breadcrumbs hidden-xs hidden-sm',
            'content_div_css':
            'container body-container col-xs-12 col-lg-11 col-lg-offset-1',
            'search_query': search_query,
            'search_results': search_results,
            'search_picks': search_picks,
            'page_unit': str(unit),
            'page_location': location,
            'address': location_and_hours['address'],
            'chat_url': get_unit_chat_link(unit, request),
            'chat_status': get_chat_status('uofc-ask'),
            'chat_status_css': get_chat_status_css('uofc-ask'),
            'hours_page_url': home_page.get_hours_page(request),
            'self': {
                'title': 'Search Results'
            }
        })
