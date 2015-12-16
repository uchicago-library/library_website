from __future__ import unicode_literals

from base.models import BasePage
from wagtail.wagtailcore.models import Page

from group.models import GroupIndexPage
from intranetunits.models import IntranetUnitsIndexPage
from news.models import NewsIndexPage, NewsPage

class IntranetHomePage(BasePage):
    content_panels = Page.content_panels + BasePage.content_panels

    subpage_types = ['base.IntranetPlainPage', 'intranetunits.IntranetUnitsIndexPage', 'group.GroupIndexPage', 'news.NewsIndexPage', 'staff.StaffIndexPage', 'units.UnitIndexPage', 'intranettocs.TOCPage']

    def get_context(self, request):
        committees_and_groups_link = GroupIndexPage.objects.live()[0].url if GroupIndexPage.objects.live().exists() else []
        departments_link = IntranetUnitsIndexPage.objects.live()[0].url if IntranetUnitsIndexPage.objects.live().exists() else []
        news_link = NewsIndexPage.objects.live()[0].url if NewsIndexPage.objects.live().exists() else []
        news_index_page = NewsIndexPage.objects.live()[0] if NewsIndexPage.objects.live().exists() else []

        news_pages = []
        if NewsIndexPage.objects.exists():
            for news_page in NewsPage.objects.live():
                # is it that get_descendants gets the page, but not the object?
                # author or published by person.
                # story date or page date. 
                news_pages.append({
                    #'story_date': news_page.story_date.strftime('%B %d').replace(' 0', ' '),
                    'story_date': '',
                    #'author_title': news_page.author.title,
                    'author_title': '',
                    #'author_url': news_page.author.url,
                    'author_url': '',
                    'excerpt': news_page.excerpt,
                    'title': news_page.title,
                    'url': news_page.url
                })

        context = super(IntranetHomePage, self).get_context(request)
        context['human_resources_link'] = '#'
        context['departments_link'] = departments_link
        context['committees_and_groups_link'] = committees_and_groups_link
        context['documents_and_policies_link'] = '#'
        context['forms_link'] = '#'
        context['technical_support_link'] = '#'
        context['news_link'] = news_link
        context['news_pages'] = news_pages
        return context
