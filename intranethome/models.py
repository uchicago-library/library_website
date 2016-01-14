from __future__ import unicode_literals

from datetime import datetime

from base.models import BasePage
from wagtail.wagtailcore.models import Page

from group.models import GroupIndexPage
from intranetunits.models import IntranetUnitsIndexPage
from news.models import get_stories_by_page, get_story_summary, NewsIndexPage, NewsPage
from staff.models import StaffPage

class IntranetHomePage(BasePage):
    content_panels = Page.content_panels + BasePage.content_panels

    subpage_types = ['base.IntranetPlainPage', 'intranetunits.IntranetUnitsIndexPage', 'group.GroupIndexPage', 'news.NewsIndexPage', 'staff.StaffIndexPage', 'units.UnitIndexPage', 'intranettocs.TOCPage']

    def get_context(self, request):
        committees_and_groups_link = GroupIndexPage.objects.live()[0].url if GroupIndexPage.objects.live().exists() else []
        departments_link = IntranetUnitsIndexPage.objects.live()[0].url if IntranetUnitsIndexPage.objects.live().exists() else []
        news_link = NewsIndexPage.objects.live()[0].url if NewsIndexPage.objects.live().exists() else []
        news_index_page = NewsIndexPage.objects.live()[0] if NewsIndexPage.objects.live().exists() else []

        sticky_pages = get_stories_by_page(1, sticky=True)
        news_pages = get_stories_by_page(1)

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
