from django.db import models
from wagtail.wagtailcore.models import Page
from wagtail.wagtailadmin.edit_handlers import FieldPanel

class GroupCommitteePage(Page):
    """
    Content type for group and committee pages.
    """
    description = models.TextField(null=True, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('description')
    ]
