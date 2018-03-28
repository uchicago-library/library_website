from django.db import models
from base.models import PublicBasePage
from wagtail.core.models import Page
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.api import APIField

class AlertPage(PublicBasePage):
    """
    Page for displaying alert messages.
    """
    INFO = 'alert-info'
    HIGH = 'alert-high'
    ALERT_TYPES = (
        (INFO, 'Informational Alert'),
        (HIGH, 'Critical Alert'),
    )

    banner_message = RichTextField(blank=False)
    more_info = RichTextField(blank=True)
    alert_level = models.CharField(
        max_length=25, 
        choices=ALERT_TYPES, 
        default=INFO,
    )

    content_panels = Page.content_panels + [
        FieldPanel('banner_message'),
        FieldPanel('more_info'),
        FieldPanel('alert_level'),
    ] + PublicBasePage.content_panels

    subpage_types = []

    api_fields = [
        APIField('banner_message'),
        APIField('more_info'),
        APIField('alert_level'),
        APIField('url'),
    ]

    search_fields = PublicBasePage.search_fields

class AlertIndexPage(PublicBasePage):
    """
    Container page for holding alert pages.
    """
    content_panels = Page.content_panels + PublicBasePage.content_panels
    subpage_types = ['alerts.AlertPage']
    search_fields = PublicBasePage.search_fields
