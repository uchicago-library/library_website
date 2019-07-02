from django import template

register = template.Library()


@register.inclusion_tag('lib_news/author.html')
def get_author(staff, unit, text, maintainer):
    return {
        'staff': staff,
        'unit': unit,
        'text': text,
        'maintainer': maintainer
    }
