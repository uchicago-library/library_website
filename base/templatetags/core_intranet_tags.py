from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def breadcrumbs(context, page):

    b = "</p>"
    while True:
        b = " &gt; <a href='" + page.url + "'>" + page.title + "</a>" + b
        if hasattr(page, "parent"):
            page = page.parent
        else:
            b = "<p><a href='/'>Home</a>" + b
            break

    return b
