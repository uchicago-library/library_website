from django import template

register = template.Library()


@register.inclusion_tag('lib_news/author.html')
def get_author(author, text, maintainer):
    return {
        'author': author,
        'text': text,
        'maintainer': maintainer
    }
