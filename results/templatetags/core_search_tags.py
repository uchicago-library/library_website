import re

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

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



