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
    # Wagtail convention for excluding page from admin interface.
    # IMPORTANT: is_abstract changes to is_creatable in wagtail 1.1.
    is_abstract = True
    
    # Fields 
    description = models.TextField(null=True, blank=True)
    last_reviewed = models.DateTimeField('Last Reviewed', 
       null=True, blank=True)
    location = models.ForeignKey('public.LocationPage', 
        null=True, blank=True, on_delete=models.SET_NULL, limit_choices_to={'is_building': True})

    # Searchable fields
    search_fields = Page.search_fields + (
        index.SearchField('description'),
    )

    content_panels = Page.content_panels + [
        FieldPanel('description'),
        FieldPanel('last_reviewed', None),
        FieldPanel('location'),
    ]

    class Meta:
        abstract = True
