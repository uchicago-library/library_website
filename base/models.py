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
    # Fields 
    description = models.TextField(null=False, blank=True)
    last_reviewed = models.DateTimeField('Last Reviewed', 
        null=True, blank=True)
    location = models.ForeignKey('public.LocationPage', 
        null=True, blank=True, on_delete=models.SET_NULL, limit_choices_to={'is_building': True}, 
        related_name='%(app_label)s_%(class)s_related')

    # Searchable fields
    search_fields = Page.search_fields + (
        index.SearchField('description'),
    )

    class Meta:
        abstract = True
