import re

from django import template
from django.template.defaultfilters import stringfilter

from lib_news.models import LibNewsIndexPage

register = template.Library()


@register.simple_tag(name="pagetype", takes_context=True)
def pagetype(context, page):
    """
    Returns the top-level section/category for display in search results.
    For LibGuides content, returns 'Research Guide' or 'Database'.
    For Wagtail pages, uses page hierarchy to determine the category,
    with special handling for news pages.
    """
    try:
        label = None

        # Check if this is LibGuides content (has searchable_content attribute)
        if hasattr(page, "searchable_content"):
            if page.searchable_content == "guides":
                label = "Research Guide"
            elif page.searchable_content == "assets":
                label = "Database"
        else:
            # Wagtail page logic
            # Special case: LibNewsIndexPage and its descendants should always show "News"
            try:
                lib_news_index = LibNewsIndexPage.objects.first()
                if lib_news_index and (
                    page.id == lib_news_index.id
                    or page.is_descendant_of(lib_news_index)
                ):
                    label = "News"
            except:  # noqa: E722
                pass

            # Get ancestors excluding root (id=1) and Home page (depth <= 2)
            if not label:
                ancestors = page.get_ancestors(inclusive=False).filter(depth__gt=2)
                if ancestors.exists():
                    # Get the first child of Home (the top-level section)
                    top_level = ancestors.first()
                    label = top_level.title

        # Return formatted span with the label
        if label:
            return f"<span class='page-type-label'>{label}</span>"
        return ""
    except:  # noqa: E722
        return ""


@register.simple_tag(name="pagepath")
def pagepath(page):
    return " > ".join(
        list(page.get_ancestors(True).exclude(id=1).values_list("title", flat=True))
    )


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
