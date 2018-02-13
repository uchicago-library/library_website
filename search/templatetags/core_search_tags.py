import re

from django import template
from django.template.defaultfilters import stringfilter
from base.models import IntranetPlainPage
from group.models import GroupIndexPage, GroupPage
from intranettocs.models import TOCPage
from intranetunits.models import IntranetUnitsIndexPage, IntranetUnitsPage
from news.models import NewsIndexPage, NewsPage
from staff.models import StaffIndexPage, StaffPage

register = template.Library()

@register.simple_tag(name='pagetype', takes_context=True)
def pagetype(context, page):
    if page.is_descendant_of(GroupIndexPage.objects.first()):
        return "<span class='g-search'>Groups</span>"
    elif page.is_descendant_of(IntranetUnitsIndexPage.objects.first()):
        return "<span class='dept-search'>Departments</span>"
    elif page.is_descendant_of(NewsIndexPage.objects.first()):
        return "<span class='n-search'>News</span>"
    elif page.is_descendant_of(StaffIndexPage.objects.first()):
        return "<span class='s-search'>Staff</span>"
    elif page.is_descendant_of(TOCPage.objects.get(title='Forms')):
        return "<span class='f-search'>Forms</span>"
    elif page.is_descendant_of(TOCPage.objects.get(title='Documents & Policies')):
        return "<span class='doc-search'>Documents</span>"
    elif page.is_descendant_of(TOCPage.objects.get(title='Technical Support')):
        return "<span class='tech-search'>Tech Support</span>"
    elif page.is_descendant_of(TOCPage.objects.get(title='Human Resources')):
        return "<span class='hr-search'>HR</span>"
    else:
        return ""

@register.simple_tag(name='pagepath')
def pagepath(page):
    return " > ".join(list(page.get_ancestors(True).exclude(id=1).values_list('title', flat=True)))

@register.filter
@stringfilter
def snippet(value):
    value = re.sub(r"<br/>", " ", value)
    value = re.sub(r"</li>", " ", value)
    value = re.sub(r"</p>", " ", value)
    value = re.sub(r"<[^>]*>", "", value)
    value = re.sub(r"[ ]+", " ", value)
    words = value.split(" ")
    value = " ".join(words[:50])
    if len(words) > 50:
        return value + "..."
    else:
        return value



