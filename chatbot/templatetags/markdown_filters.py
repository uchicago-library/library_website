import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def markdown_to_html(value):
    """
    Convert markdown text to HTML.
    Usage: {{ text|markdown_to_html }}
    """
    if value:
        # Convert markdown to HTML with extensions for formatting
        html = markdown.markdown(
            value,
            extensions=[
                'markdown.extensions.fenced_code',  # Allow code blocks with ```
                'markdown.extensions.tables',  # Support for tables
                'markdown.extensions.nl2br',  # Convert newlines to <br>
                'markdown.extensions.sane_lists',  # Better list handling
            ],
        )
        return mark_safe(html)
    return ""
