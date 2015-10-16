from django.db import models
from wagtail.wagtailcore.models import Page
#from wagtail.wagtailadmin.edit_handlers import FieldPanel, FieldRowPanel, MultiFieldPanel
#from wagtail.wagtailimages.blocks import ImageChooserBlock
#from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsearch import index
from base.models import BasePage

class CollectionPage(BasePage):
    """
    Pages for individual collections.
    """
    short_abstract = models.TextField(null=False, blank=False)
