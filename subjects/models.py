from django.db import models
from wagtail.wagtailsearch import index
from wagtail.wagtailsnippets.models import register_snippet
from wagtail.wagtailadmin.edit_handlers import FieldPanel

@register_snippet
class Subject(models.Model, index.Indexed):
    """
    Snippet for subjects.
    """
    name = models.CharField(max_length=255, blank=False)
    parent = models.ForeignKey(
        'self',
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
    )

    panels = [
        FieldPanel('name'),
        FieldPanel('parent'),
    ]

    def __str__(self):
        return self.name

    search_fields = [
        index.SearchField('name', partial_match=True),
    ]
