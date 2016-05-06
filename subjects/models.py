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


class SubjectSeeAlsoTable(Orderable, models.Model):
    alias = models.CharField(max_length=255)
    snippet = ParentalKey('subjects.Subject', related_name='see_also')


@register_snippet
class Subject(ClusterableModel, index.Indexed):
    """
    Snippet for subjects.
    """
    name = models.CharField(max_length=255, blank=False)

    libguide_url = models.URLField(
        max_length=255, 
        null=True, 
        blank=True)

    panels = [
        FieldPanel('name'),
        FieldPanel('libguide_url'),
        InlinePanel('parent_subject', label="Parent"),
        InlinePanel('see_also', label="Aliases")
    ]

    def get_descendants(self, include_self = True):
        subject_ids_to_check = [self.id]
        checked_subjects = []

        while subject_ids_to_check:
            s = subject_ids_to_check.pop()
            checked_subjects.append(s)
            subject_ids_to_check = subject_ids_to_check + list(SubjectParentRelations.objects.filter(parent__id=s).values_list("child", flat=True))

        if not include_self: 
            checked_subjects.remove(self.id)

        return Subject.objects.filter(id__in=checked_subjects)

    def __str__(self):
        return self.name

    search_fields = [
        index.SearchField('name', partial_match=True),
    ]

    class Meta:
        ordering = ['name']


