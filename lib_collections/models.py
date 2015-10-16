from django.db import models
from wagtail.wagtailcore.models import Orderable, Page
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel
#from wagtail.wagtailimages.blocks import ImageChooserBlock
#from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsearch import index
from wagtail.wagtailsnippets.models import register_snippet
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

# Collection page content type
class CollectionPage(BasePage):
    """
    Pages for individual collections.
    """
    short_abstract = models.TextField(null=False, blank=False)

    content_panels = Page.content_panels + [
        FieldPanel('short_abstract'),
        InlinePanel('access_links', label="Access Links"),
    ]
