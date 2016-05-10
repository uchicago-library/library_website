from django import template

register = template.Library()

@register.inclusion_tag('lib_collections/collections_formats.html')
def collections_formats(collection_page):
    formats = []
    for c in collection_page.collection_placements.all():
        formats.append(c.format.text)

    formats.sort()

    # 'Digital' should be the first, no matter what. 
    if 'Digital' in formats:
        formats.remove('Digital')
        formats = ['Digital'] + formats

    return {
        'formats': formats
    }

