from django.shortcuts import render

from department.models import DepartmentIndexPage
from group.models import GroupIndexPage

from news.models import NewsIndexPage

import datetime, string

def index(request):
    committees_and_groups_link = GroupIndexPage.objects.all()[0].url
    departments_link = DepartmentIndexPage.objects.all()[0].url

    news_index_page = NewsIndexPage.objects.all()[0]

    news_pages = []
    for child in news_index_page.get_descendants():
        news_pages.append({
            'date':  child.first_published_at.strftime('%B %d').replace(' 0', ' '),
            'title': child.title,
            'url':   child.url
        })

    return render(request, 'intranethome/intranet_home_page.html', {
        'human_resources_link': '#',
        'departments_link': departments_link,
        'committees_and_groups_link': committees_and_groups_link,
        'documents_and_policies_link': '#',
        'forms_link': '#',
        'technical_support_link': '#',
        'news_pages': news_pages
    })
