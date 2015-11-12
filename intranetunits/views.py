from django.contrib.contenttypes.models import ContentType 
from django.shortcuts import render 
from intranetunits.models import IntranetUnitsPage, IntranetUnitsIndexPage
from base.views import breadcrumbs

# build a tree to hold department titles, links and subunits. 
def get_tree(page):
    department_content_type = ContentType.objects.get_for_model(IntranetUnitsPage).pk

    children = []
    for child in sorted(page.get_children().filter(content_type=department_content_type), key=lambda page: page.title):
        children.append(get_tree(child))

    return {
        'title':    page.title,
        'url':      page.url,
        'children': children
    }

def index(request):
    try:
        intranetunits_index_page = IntranetUnitsIndexPage.objects.all()[0]
        units = get_tree(intranetunits_index_page)

    except IndexError:
        raise Exception('IntranetUnits Index Page does not exist.')

    return render(request, 'intranetunits/intranetunits_index_page.html', {
        'breadcrumbs': breadcrumbs(request),
        'units': units,
        'self': {
            'intro': intranetunits_index_page.intro,
            'title': intranetunits_index_page.title
        }
    })
        
        
