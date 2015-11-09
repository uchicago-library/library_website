from django.db import models
from wagtail.wagtailcore.models import Page
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailsearch import index

class IntranetBasePage(Page):
    """
    Adds additional fields to the wagtail Page model.
    Most other content types should extend this model
    instead of Page.
    """
    # Fields 
    last_reviewed = models.DateTimeField(
        'Last Reviewed', 
        null=True, 
        blank=True
    )

    page_maintainer = models.ForeignKey(
        'staff.StaffPage',
        null=True, 
        blank=False, 
        on_delete=models.SET_NULL,
        related_name='%(app_label)s_%(class)s_maintainer'
    )

    editor = models.ForeignKey(
        'staff.StaffPage',
        null=True, 
        blank=False, 
        on_delete=models.SET_NULL,
        related_name='%(app_label)s_%(class)s_editor'
    )

    # Searchable fields
    search_fields = Page.search_fields + (
        index.SearchField('description'),
    )

    content_panels = [
        MultiFieldPanel(
            [
                FieldPanel('page_maintainer'),
                FieldPanel('editor'),
                FieldPanel('last_reviewed', None),
            ],
            heading='Page Management'
        ),
    ]

    class Meta:
        abstract = True

class PlainPage(IntranetBasePage):
    body = RichTextField()

    subpage_types = ['intranetbase.PlainPage', 'intranetbase.SidebarPage']

PlainPage.content_panels = Page.content_panels + [
    FieldPanel('body')
] + IntranetBasePage.content_panels

class SidebarPage(IntranetBasePage):
    body = RichTextField()

    subpage_types = ['intranetbase.PlainPage', 'intranetbase.SidebarPage']

SidebarPage.content_panels = Page.content_panels + [
    FieldPanel('body')
] + IntranetBasePage.content_panels
