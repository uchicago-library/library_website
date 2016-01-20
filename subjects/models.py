from django.db import models
from wagtail.wagtailsearch import index
from wagtail.wagtailsnippets.models import register_snippet
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel
from wagtail.wagtailsnippets.edit_handlers import SnippetChooserPanel
from wagtail.wagtailcore.models import Orderable
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel

class SubjectParentRelations(Orderable, models.Model):
    """
    Through table for capturing subjects with multiple
    parent subjects.
    """
    child = ParentalKey('subjects.Subject', related_name='parent_subject') # Yeah, this is weird but it works
    parent = models.ForeignKey('subjects.Subject', related_name='+')

    panels = [
        SnippetChooserPanel('parent'),
    ]


@register_snippet
class Subject(ClusterableModel, index.Indexed):
    """
    Snippet for subjects.
    """
    name = models.CharField(max_length=255, blank=False)

    panels = [
        FieldPanel('name'),
        InlinePanel('parent_subject', label="Parent"),
    ]

    def __str__(self):
        return self.name

    search_fields = [
        index.SearchField('name', partial_match=True),
    ]


