from django import template

register = template.Library()


@register.inclusion_tag('public/contacts_in_sidebar.html')
def list_contacts_in_sidebar(contacts=[], title='Contact'):
    return {'contacts': contacts, 'sect_title': title}


@register.inclusion_tag('public/related_exhibits.html')
def get_related_exhibits(exhibits=[]):
    return {'exhibits': exhibits}
