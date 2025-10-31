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
    """
    Returns a formatted page type label for display in search results.
    Uses Wagtail's content type to dynamically determine the page type.
    """
    try:
        # Get the content type name and convert to title case
        content_type_name = page.get_content_type().name
        # Convert to title case (e.g., "exhibit page" -> "Exhibit Page")
        page_type_label = content_type_name.title()

        # Return formatted span with the page type
        return f"<span class='page-type-label'>{page_type_label}</span>"
    except:
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



