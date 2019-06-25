from django import template

register = template.Library()


@register.inclusion_tag('lib_collections/exhibit_results.html')
def show_exhibits(exhibits=None, title='Exhibits'):
    return {'exhibits': exhibits, 'sect_title': title}
