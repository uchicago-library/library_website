from django.shortcuts import render

from news.models import NewsIndexPage

def index(request):
    news_index_page = NewsIndexPage.objects.all()[0]

    news_pages = []
    for child in news_index_page.get_descendants():
        news_pages.append({
            'date':  child.first_published_at.strftime('%B %d').replace(' 0', ' '),
            'title': child.title,
            'url':   child.url
        })

    return render(request, 'news/news_index_page.html', {
        'news_pages': news_pages,
        'self': {
            'intro': news_index_page.intro,
            'title': news_index_page.title
        }
    })
