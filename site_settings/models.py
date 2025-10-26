from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.models import Orderable


@register_setting(icon="warning")
class EmergencyHours(BaseSiteSetting):
    enable = models.BooleanField(
        default=False,
        help_text='Checking this box will enable "Emergency Hours" and \
                   replace the hours dropdown in the public website header',
    )
    link_text = models.CharField(
        max_length=35,
        blank=True,
        help_text='Optional hours link text to display in the header. \
                   Defaults to "View Hours" if nothing is set',
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("enable"),
                FieldPanel("link_text"),
            ],
            heading="Emergency Hours",
        )
    ]


@register_setting(icon="mail")
class ContactInfo(BaseSiteSetting):
    report_a_problem = models.URLField(
        max_length=200,
        null=False,
        blank=False,
        default=(
            "https://www.lib.uchicago.edu/research/help/ask-librarian/ask-contact/"
        ),
    )

    panels = [
        FieldPanel("report_a_problem"),
    ]


class ExcludedCNetID(Orderable, models.Model):
    """
    CNetID to exclude from staff directory sync.
    """

    settings = ParentalKey(
        'StaffSyncSettings', on_delete=models.CASCADE, related_name='excluded_cnetids'
    )
    cnetid = models.CharField(
        max_length=25, help_text='CNetID to exclude from staff directory sync'
    )
    note = models.CharField(
        max_length=300,
        blank=True,
        help_text='Optional note explaining why this person is excluded from sync',
    )

    panels = [
        FieldPanel('cnetid'),
        FieldPanel('note'),
    ]

    def __str__(self):
        return self.cnetid


@register_setting(icon="user")
class StaffSyncSettings(BaseSiteSetting, ClusterableModel):
    """
    Settings for staff directory synchronization.
    """

    panels = [
        InlinePanel('excluded_cnetids', label="Excluded CNetIDs"),
    ]
