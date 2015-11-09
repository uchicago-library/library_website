from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render

from department.models import DepartmentPage, DepartmentIndexPage
from intranetbase.views import breadcrumbs

# build a tree to hold department titles, links and subdepartments. 
def get_tree(page):
    department_content_type = ContentType.objects.get_for_model(DepartmentPage).pk

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
        department_index_page = DepartmentIndexPage.objects.all()[0]
        departments = get_tree(department_index_page)

    except IndexError:
        raise Exception('Department Index Page does not exist.')

    return render(request, 'department/department_index_page.html', {
        'breadcrumbs': breadcrumbs(request),
        'departments': departments,
        'self': {
            'intro': department_index_page.intro,
            'title': department_index_page.title
        }
    })
        
        
