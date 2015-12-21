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
    # add class g-search.
    if type(page.specific_class()) is GroupPage:
        return 'Groups'
    elif type(page.specific_class()) is IntranetPlainPage:
        return 'Loop Page'
    # add class dept-search
    elif type(page.specific_class()) is IntranetUnitsPage:
        return 'Departments'
    elif type(page.specific_class()) is NewsPage:
        return 'News Page'
    # add class staff-search
    elif type(page.specific_class()) is StaffPage:
        return 'Staff'
    else:
        return 'Unknown page type'

    # add class f-search, "Forms"
    # add class doc-search "Documents"
    # add class tech-search "Tech Support"
    # add class hr-search "HR"

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



