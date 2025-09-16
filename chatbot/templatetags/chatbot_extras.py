from django import template

register = template.Library()


@register.filter
def page_type(value):
    """Return the class name of an object in templates.

    Usage: {{ some_obj|page_type }}
    """
    try:
        return value.__class__.__name__
    except Exception:
        return ''
