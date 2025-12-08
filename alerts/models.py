from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.fields import RichTextField
from wagtail.models import Page

from base.models import PublicBasePage


class AlertPage(PublicBasePage):
    """
    Page for displaying alert messages.
    """

    INFO = "alert-info"
    LOW = "alert-low"
    HIGH = "alert-high"
    ALERT_TYPES = (
        (INFO, "Informational Alert"),
        (LOW, "General Alert"),
        (HIGH, "Critical Alert"),
    )

    banner_message = RichTextField(blank=False)
    more_info = RichTextField(blank=True)
    alert_level = models.CharField(
        max_length=25,
        choices=ALERT_TYPES,
        default=INFO,
    )

    content_panels = (
        Page.content_panels
        + [
            FieldPanel("banner_message"),
            FieldPanel("more_info"),
            FieldPanel("alert_level"),
        ]
        + PublicBasePage.content_panels
    )

    subpage_types = []

    api_fields = [
        APIField("banner_message"),
        APIField("more_info"),
        APIField("alert_level"),
        APIField("url"),
    ]

    search_fields = PublicBasePage.search_fields


class AlertIndexPage(PublicBasePage):
    """
    Container page for holding alert pages.
    """

    max_count = 1
    content_panels = Page.content_panels + PublicBasePage.content_panels
    subpage_types = ["alerts.AlertPage"]
    search_fields = PublicBasePage.search_fields
