from django.db import models
from django import forms
from django.utils import timezone
from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailsearch import index

class BasePage(Page):
    """
    Adds additional fields to the wagtail Page model.
    Most other content types should extend this model
    instead of Page.
    """
    is_abstract = True
    description = models.TextField()
    last_reviewed = models.DateTimeField('Last Reviewed', 
       null=True, blank=True)

    # Searchable fields
    search_fields = Page.search_fields + (
        index.SearchField('description'),
    )

BasePage.content_panels = Page.content_panels + [
    FieldPanel('description'),
    FieldPanel('last_reviewed', None),
]

