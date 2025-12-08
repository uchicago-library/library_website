from django.core.cache import caches
from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.models import Orderable, Site
from wagtail.search import index
from wagtail.snippets.models import register_snippet


class SubjectParentRelations(Orderable, models.Model):
    """
    Through table for capturing subjects with multiple
    parent subjects.
    """

    child = ParentalKey(
        "subjects.Subject", on_delete=models.CASCADE, related_name="parent_subject"
    )  # Yeah, this is weird but it works
    parent = models.ForeignKey(
        "subjects.Subject", on_delete=models.CASCADE, related_name="+"
    )

    panels = [
        FieldPanel("parent"),
    ]


class SubjectSeeAlsoTable(Orderable, models.Model):
    alias = models.CharField(max_length=255)
    snippet = ParentalKey("subjects.Subject", related_name="see_also")


@register_snippet
class Subject(ClusterableModel, index.Indexed):
    """
    Snippet for subjects.
    """

    name = models.CharField(max_length=255, blank=False)

    libguide_url = models.URLField(max_length=255, null=True, blank=True)

    display_in_dropdown = models.BooleanField(default=False)

    panels = [
        FieldPanel("name"),
        FieldPanel("libguide_url"),
        InlinePanel("parent_subject", label="Parent"),
        InlinePanel("see_also", label="Aliases"),
        FieldPanel("display_in_dropdown"),
    ]

    def get_descendants(self, include_self=True):
        subject_ids_to_check = [self.id]
        checked_subjects = []

        relations_cache = caches["default"]

        while subject_ids_to_check:
            s = subject_ids_to_check.pop()
            checked_subjects.append(s)

            key = "parent_" + str(s)

            ids_to_add = relations_cache.get(key)

            if not ids_to_add:
                ids_to_add = list(
                    SubjectParentRelations.objects.filter(parent__id=s).values_list(
                        "child", flat=True
                    )
                )
                relations_cache.set(key, ids_to_add, 60 * 5)

            subject_ids_to_check = subject_ids_to_check + ids_to_add

        if not include_self:
            checked_subjects.remove(self.id)

        return Subject.objects.filter(id__in=checked_subjects)

    def get_collecting_area_page_url(self, request):
        """
        Get the relative url to a CollectingAreaPage.

        Args:
            request: object

        Returns:
            string, relative url
        """
        current_site = Site.find_for_request(request)
        collecting_area_page = self.lib_collections_collectingareapage_related.first()
        url = ""
        if collecting_area_page and collecting_area_page.live:
            url = collecting_area_page.relative_url(current_site)
        return url

    @staticmethod
    def get_top_level_subjects():
        return Subject.objects.filter(parent_subject=None)

    def get_children(self):
        return Subject.objects.filter(parent_subject__parent=self)

    def __str__(self):
        return self.name

    search_fields = [
        index.AutocompleteField("name"),
    ]

    class Meta:
        ordering = ["name"]
