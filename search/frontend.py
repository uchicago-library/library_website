from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import JsonResponse
from django.shortcuts import render
from wagtail import Site, models
from wagtail.contrib.search_promotions.models import Query


def search(
    request,
    template=None,
    template_ajax=None,
    results_per_page=10,
    use_json=False,
    json_attrs=['title', 'url'],
    show_unpublished=False,
    search_title_only=False,
    extra_filters={},
    path=None,
):

    # Get default templates
    if template is None:
        if hasattr(settings, 'WAGTAILSEARCH_RESULTS_TEMPLATE'):
            template = settings.WAGTAILSEARCH_RESULTS_TEMPLATE
        else:
            template = 'wagtailsearch/search_results.html'

    if template_ajax is None:
        if hasattr(settings, 'WAGTAILSEARCH_RESULTS_TEMPLATE_AJAX'):
            template_ajax = settings.WAGTAILSEARCH_RESULTS_TEMPLATE_AJAX
        else:
            template_ajax = template

    # Get query string and page from GET paramters
    query_string = request.GET.get('q', '')
    page = request.GET.get('page', request.GET.get('p', 1))

    # Search
    if query_string != '':
        site = Site.find_for_request(request)
        pages = models.Page.objects.filter(
            path__startswith=(path or site.root_page.path)
        )

        if not show_unpublished:
            pages = pages.live()

        if extra_filters:
            pages = pages.filter(**extra_filters)

        if search_title_only:
            search_results = pages.search(query_string, fields=['title'])
        else:
            search_results = pages.search(query_string)

        # Get query object
        query = Query.get(query_string)

        # Add hit
        query.add_hit()

        # Pagination
        paginator = Paginator(search_results, results_per_page)
        try:
            search_results = paginator.page(page)
        except PageNotAnInteger:
            search_results = paginator.page(1)
        except EmptyPage:
            search_results = paginator.page(paginator.num_pages)
    else:
        query = None
        search_results = None

    if use_json:
        # Return a json response
        if search_results:
            search_results_json = []
            for result in search_results:
                result_specific = result.specific

                search_results_json.append(
                    dict(
                        (attr, getattr(result_specific, attr))
                        for attr in json_attrs
                        if hasattr(result_specific, attr)
                    )
                )

            return JsonResponse(search_results_json, safe=False)
        else:
            return JsonResponse([], safe=False)
    else:  # Render a template
        if request.is_ajax() and template_ajax:
            template = template_ajax

        return render(
            request,
            template,
            dict(
                query_string=query_string,
                search_results=search_results,
                is_ajax=request.is_ajax(),
                query=query,
            ),
        )
