from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from intranethome.models import IntranetHomePage
from units.models import UnitIndexPage
from wagtail.wagtailcore.models import Page, Site
from wagtail.wagtailsearch.models import Query
from wagtail.contrib.wagtailsearchpromotions.models import SearchPromotion

def loop_search(request):
    search_query = request.GET.get('query', None)
    page = request.GET.get('page', 1)

    # Search
    search_results_count = 0

    if search_query:
        loop_homepage = Site.objects.get(site_name="Loop").root_page
        unit_index_page = UnitIndexPage.objects.first()
        search_results = Page.objects.live().descendant_of(loop_homepage, True).not_descendant_of(unit_index_page, True).search(search_query)
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

    return render(request, 'search/loop_search.html', {
        'search_query': search_query,
        'search_results': search_results,
        'search_results_count': search_results_count,
        'search_picks': search_picks,
    })
