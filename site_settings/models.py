from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSetting, register_setting


@register_setting(icon='warning')
class EmergencyHours(BaseSetting):
    enable = models.BooleanField(
        default=False,
        help_text='Checking this box will enable "Emergency Hours" and \
                   replace the hours dropdown in the public website header'
    )
    link_text = models.CharField(
        max_length=35,
        blank=True,
        help_text='Optional hours link text to display in the header. \
                   Defaults to "View Hours" if nothing is set'
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("enable"),
                FieldPanel("link_text"),
            ],
            heading="Emergency Hours"
        )
    ]
