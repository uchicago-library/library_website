from __future__ import unicode_literals

from wagtail.wagtailcore.models import Page

class IntranetHomePage(Page):
    subpage_types = ['intranetunits.IntranetUnitsIndexPage', 'group.GroupIndexPage', 'news.NewsIndexPage', 'staff.StaffIndexPage']
