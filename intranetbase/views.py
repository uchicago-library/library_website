from django.shortcuts import render

def breadcrumbs(request):
    breadcrumbs = [{
        "href": "/",
        "text": "Home"
    }]

    path_components = [component for component in request.path.split('/') if component]
    page, args, kwargs = request.site.root_page.specific.route(request, path_components)
    while page:
        breadcrumbs.append({
            "href": page.url,
            "text": page.title
        })
        if hasattr(page, 'parent'):
            page = page.parent
        else:
            break

    return breadcrumbs
