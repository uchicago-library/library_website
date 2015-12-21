from __future__ import unicode_literals

from datetime import datetime

from base.models import BasePage
from wagtail.wagtailcore.models import Page

from group.models import GroupIndexPage
from intranetunits.models import IntranetUnitsIndexPage
from news.models import NewsIndexPage, NewsPage
from staff.models import StaffPage

class IntranetHomePage(BasePage):
    content_panels = Page.content_panels + BasePage.content_panels

    subpage_types = ['base.IntranetPlainPage', 'intranetunits.IntranetUnitsIndexPage', 'group.GroupIndexPage', 'news.NewsIndexPage', 'staff.StaffIndexPage', 'units.UnitIndexPage', 'intranettocs.TOCPage']

    def get_context(self, request):
        committees_and_groups_link = GroupIndexPage.objects.live()[0].url if GroupIndexPage.objects.live().exists() else []
        departments_link = IntranetUnitsIndexPage.objects.live()[0].url if IntranetUnitsIndexPage.objects.live().exists() else []
        news_link = NewsIndexPage.objects.live()[0].url if NewsIndexPage.objects.live().exists() else []
        news_index_page = NewsIndexPage.objects.live()[0] if NewsIndexPage.objects.live().exists() else []

        sticky_pages = []
        for sticky_page in NewsPage.objects.live().exclude(sticky_until=None):

            # skip sticky stories that have 'expired'.
            if sticky_page.sticky_until and datetime.date(datetime.now()) > sticky_page.sticky_until:
                continue

            day = int(sticky_page.story_date.strftime('%d'))
            if 4 <= day <= 20 or 24 <= day <= 30:
                suffix = "th"
            else:
                suffix = ["st", "nd", "rd"][day % 10 - 1]

            if sticky_page.author:
                author_title = sticky_page.author.title
                author_url = sticky_page.author.url
            else:
                cnetid = sticky_page.owner.username
                author_title = StaffPage.objects.get(cnetid=cnetid).title
                author_url = StaffPage.objects.get(cnetid=cnetid).url

            sticky_pages.append({
                'story_date_sort': sticky_page.story_date,
                'story_date': sticky_page.story_date.strftime('%B %d').replace(' 0', ' ') + suffix,
                'author_title': author_title,
                'author_url': author_url,
                'excerpt': sticky_page.excerpt,
                'title': sticky_page.title,
                'url': sticky_page.url,
                'body': sticky_page.body
            })
        sticky_pages = sorted(sticky_pages, key=lambda p: p['story_date_sort'] )
        if sticky_pages:
            sticky_pages = [sticky_pages.pop(0)]

        news_pages = []
        for news_page in NewsPage.objects.live():
            # skip stories that are in the future. 
            if news_page.story_date > datetime.date(datetime.now()):
                continue

            # skip active sticky stories. 
            if news_page.sticky_until and datetime.date(datetime.now()) < news_page.sticky_until:
                continue

            day = int(news_page.story_date.strftime('%d'))
            if 4 <= day <= 20 or 24 <= day <= 30:
                suffix = "th"
            else:
                suffix = ["st", "nd", "rd"][day % 10 - 1]

            if news_page.author:
                author_title = news_page.author.title
                author_url = news_page.author.url
            else:
                cnetid = news_page.owner.username
                author_title = StaffPage.objects.get(cnetid=cnetid).title
                author_url = StaffPage.objects.get(cnetid=cnetid).url

            news_pages.append({
                'story_date_sort': news_page.story_date,
                'story_date': news_page.story_date.strftime('%B %d').replace(' 0', ' ') + suffix,
                'author_title': author_title,
                'author_url': author_url,
                'excerpt': news_page.excerpt,
                'title': news_page.title,
                'url': news_page.url,
                'body': news_page.body
            })
        news_pages = sorted(news_pages, key=lambda p: p['story_date_sort'] )

        context = super(IntranetHomePage, self).get_context(request)
        context['human_resources_link'] = '#'
        context['departments_link'] = departments_link
        context['committees_and_groups_link'] = committees_and_groups_link
        context['documents_and_policies_link'] = '#'
        context['forms_link'] = '#'
        context['technical_support_link'] = '#'
        context['news_link'] = news_link
        context['sticky_pages'] = sticky_pages
        context['news_pages'] = news_pages
        return context
