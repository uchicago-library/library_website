from django.db import models
from base.models import PublicBasePage
from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel

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
        'banner_message',
        'more_info',
        'alert_level',
    ]


class AlertIndexPage(PublicBasePage):
    """
    Container page for holding alert pages.
    """
    content_panels = Page.content_panels + PublicBasePage.content_panels
    subpage_types = ['alerts.AlertPage']
