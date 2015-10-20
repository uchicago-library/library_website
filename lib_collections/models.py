from django.db import models
from wagtail.wagtailcore.models import Orderable, Page
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel
from wagtail.wagtailsearch import index
from wagtail.wagtailsnippets.models import register_snippet
from wagtail.wagtailsnippets.edit_handlers import SnippetChooserPanel
from modelcluster.fields import ParentalKey
from base.models import BasePage

# The abstract model for related links, complete with panels
class AccessLink(models.Model):
    access_link_label = models.CharField(max_length=255)
    access_link_url = models.URLField("Access link URL", blank=False)

    panels = [
        FieldPanel('access_link_label'),
        FieldPanel('access_link_url'),
    ]

    class Meta:
        abstract = True

# The real model which combines the abstract model, an
# Orderable helper class, and what amounts to a ForeignKey link
# to the model we want to add related links to (CollectionPage)
class CollectionPageAccessLinks(Orderable, AccessLink):
    page = ParentalKey('lib_collections.CollectionPage', related_name='access_links')


# Model for format strings to be used on collection pages
@register_snippet
class Format(models.Model, index.Indexed):
    text = models.CharField(max_length=255, blank=False)

    panels = [
        FieldPanel('text'),
    ]

    def __str__(self):
        return self.text

    search_fields = [
        index.SearchField('text', partial_match=True),
    ]

# Interstitial model for linking the Format model to the CollectionPage
class CollectionPageFormatPlacement(Orderable, models.Model):
    page = ParentalKey('lib_collections.CollectionPage', related_name='collection_placements')
    format = models.ForeignKey('lib_collections.Format', related_name='+')

    class Meta:
        verbose_name = "Collection Placement"
        verbose_name_plural = "Collection Placements"

    panels = [
        SnippetChooserPanel('format'),
    ]

    def __str__(self):
        return self.page.title + " -> " + self.format.text

# Collection page content type
class CollectionPage(BasePage):
    """
    Pages for individual collections.
    """
    short_abstract = models.TextField(null=False, blank=False)

    content_panels = Page.content_panels + [
        FieldPanel('short_abstract'),
        InlinePanel('collection_placements', label="Format"),
        InlinePanel('access_links', label="Access Links"),
    ]
