from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from wagtail.wagtailcore.models import Page, Site
from wagtail.wagtailsearch.models import Query
from wagtail.contrib.wagtailsearchpromotions.models import SearchPromotion
from public.models import StandardPage
from library_website.settings import PUBLIC_HOMEPAGE
from base.utils import get_hours_and_location
from ask_a_librarian.utils import get_chat_status, get_chat_status_css, get_unit_chat_link

def results(request):
    search_query = request.GET.get('query', None)
    page = request.GET.get('page', 1)

    # Search
    if search_query:
        homepage = Site.objects.get(site_name="Public").root_page
        search_results = Page.objects.live().descendant_of(homepage).search(search_query)
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

    return render(request, 'results/results.html', {
        'content_div_css': 'container body-container col-xs-12 col-lg-11 col-lg-offset-1',
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
    })
