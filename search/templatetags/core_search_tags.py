import re

from django import template
from django.template.defaultfilters import stringfilter
from base.models import IntranetPlainPage
from group.models import GroupPage
from intranetunits.models import IntranetUnitsPage
from news.models import NewsPage
from staff.models import StaffPage

register = template.Library()

@register.simple_tag(name='pagetype', takes_context=True)
def pagetype(context, page):
    if type(page.specific_class()) is GroupPage:
        return 'Group Page'
    elif type(page.specific_class()) is IntranetPlainPage:
        return 'Loop Page'
    elif type(page.specific_class()) is IntranetUnitsPage:
        return 'Unit Page'
    elif type(page.specific_class()) is NewsPage:
        return 'News Page'
    elif type(page.specific_class()) is StaffPage:
        return 'Staff Page'
    else:
        return 'Unknown page type'

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



