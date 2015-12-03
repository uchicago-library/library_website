from __future__ import unicode_literals

from base.models import BasePage
from wagtail.wagtailcore.models import Page

class IntranetHomePage(BasePage):
    content_panels = Page.content_panels + BasePage.content_panels

    subpage_types = ['base.IntranetPlainPage', 'intranetunits.IntranetUnitsIndexPage', 'group.GroupIndexPage', 'news.NewsIndexPage', 'staff.StaffIndexPage', 'units.UnitIndexPage']
