from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render

from intranetunits.models import IntranetUnitsIndexPage
from group.models import GroupIndexPage

from news.models import NewsIndexPage, NewsPage

import datetime, string

def index(request):

    committees_and_groups_link = GroupIndexPage.objects.live()[0].url if GroupIndexPage.objects.live().exists() else []
    departments_link = IntranetUnitsIndexPage.objects.live()[0].url if IntranetUnitsIndexPage.objects.live().exists() else []
    news_link = NewsIndexPage.objects.live()[0].url if NewsIndexPage.objects.live().exists() else []
    news_index_page = NewsIndexPage.objects.live()[0] if NewsIndexPage.objects.live().exists() else []

    news_pages = []
    if NewsIndexPage.objects.exists():
        for child in news_index_page.get_descendants():
            # is it that get_descendants gets the page, but not the object?
            news_pages.append({
                'story_date': NewsPage.objects.get(pk=child.pk).story_date.strftime('%B %d').replace(' 0', ' '),
                'author_title': NewsPage.objects.get(pk=child.pk).author.title,
                'author_url': NewsPage.objects.get(pk=child.pk).author.url,
                'excerpt': NewsPage.objects.get(pk=child.pk).excerpt,
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
        'news_link': news_link,
        'news_pages': news_pages

    })
