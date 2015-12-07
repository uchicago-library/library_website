from django.utils.html import format_html
from django.conf import settings
from wagtail.wagtailcore import hooks

@hooks.register('insert_editor_css')
def editor_css():
    """
    Modify the admin css in order to hide
    option in the rich text editor etc.
    """
    return format_html('<link rel="stylesheet" href="' \
    + settings.STATIC_URL \
    + 'css/admin.scss">')
