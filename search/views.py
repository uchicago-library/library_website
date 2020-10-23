from base.wagtail_hooks import (
    get_required_groups, has_permission, redirect_users_without_permissions
)
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import redirect, render
from library_website.settings import EBOOKS_SEARCH
from units.models import UnitIndexPage
from wagtail.contrib.search_promotions.models import SearchPromotion
from wagtail.core.models import Page, Site
from wagtail.search.models import Query


def ebooks_search(request):
    """
    View for processing a form submission and forwarding
    a request to an ebooks search in the catalog.
    """
    if request.method == 'GET':
        query = request.GET.get('q')
        if not query:
            query = '*'
        return redirect(EBOOKS_SEARCH + query)


def loop_search(request):
    """
    Loop search results.
    """
    loop_homepage = Site.objects.get(site_name='Loop').root_page
    if not has_permission(request.user, get_required_groups(loop_homepage)):
        return redirect_users_without_permissions(
            loop_homepage, request, None, None
        )

    search_query = request.GET.get('query', None)
    page = request.GET.get('page', 1)

    # Search
    search_results_count = 0

    if search_query:
        unit_index_page = UnitIndexPage.objects.first()
        search_results = Page.objects.live().descendant_of(
            loop_homepage, True
        ).not_descendant_of(unit_index_page, True).search(search_query)
        search_results_count = search_results.count()
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

    return render(
        request, 'search/loop_search.html', {
            'search_query': search_query,
            'search_results': search_results,
            'search_results_count': search_results_count,
            'search_picks': search_picks,
        }
    )
