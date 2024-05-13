from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, PageChooserPanel
from wagtail.admin.edit_handlers import PageChooserPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting


@register_setting(icon='warning')
class EmergencyHours(BaseSiteSetting):
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


@register_setting(icon="mail")
class ContactInfo(BaseSiteSetting):
    report_a_problem = models.ForeignKey(
        'wagtailcore.Page', null=True,
        blank=True,
        on_delete=models.SET_NULL, related_name='+',
        help_text=("'Contact us' page for when users encounter "
                   "an error on our backend.")
    )

    panels = [
        PageChooserPanel('report_a_problem'),
    ]
