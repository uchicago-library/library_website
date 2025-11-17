from django.core.cache import cache
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.contrib.settings.models import (
    BaseGenericSetting,
    BaseSiteSetting,
    register_setting,
)
from wagtail.models import Orderable
from wagtail.snippets.models import register_snippet


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
class StaffSyncSettings(BaseGenericSetting, ClusterableModel):
    """
    Settings for staff directory synchronization.
    Applies globally across all sites.
    """

    panels = [
        InlinePanel('excluded_cnetids', label="Excluded CNetIDs"),
    ]


@register_setting(icon="doc-full")
class NewsFeedSettings(BaseGenericSetting):
    """
    Settings for the library news feed display.
    Only applies to the public site.
    """

    default_visible = models.PositiveIntegerField(
        default=9,
        help_text='Number of news items to display initially on the news index page',
    )
    increment_by = models.PositiveIntegerField(
        default=12,
        help_text='Number of additional news items to load when "Load More" is clicked',
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("default_visible"),
                FieldPanel("increment_by"),
            ],
            heading="News Feed Display Settings",
        )
    ]


class QuickNumber(Orderable, models.Model):
    """
    A phone number or link to display in directory quick numbers.
    """

    group = ParentalKey(
        'QuickNumberGroup', on_delete=models.CASCADE, related_name='numbers'
    )
    label = models.CharField(
        max_length=100,
        help_text='Display label (e.g., "Main Telephone", "Circulation")',
    )
    number = models.CharField(
        max_length=20, blank=True, help_text='Phone number (e.g., "773-702-8740")'
    )
    link = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text='Optional page link instead of phone number',
    )

    panels = [
        FieldPanel('label'),
        FieldPanel('number'),
        FieldPanel('link'),
    ]

    def __str__(self):
        return f"{self.label}: {self.number or 'link'}"


@register_snippet
class QuickNumberGroup(ClusterableModel):
    """
    Groups of quick numbers for libraries/departments in the directory.
    """

    slug = models.SlugField(
        max_length=255,
        unique=True,
        help_text='Identifier for this group (e.g., "the-joseph-regenstein-library")',
    )
    display_name = models.CharField(
        max_length=255,
        help_text='Human-readable name for this group',
    )
    is_default = models.BooleanField(
        default=False,
        help_text='Use this group as the default fallback when no specific quick numbers are found',
    )

    panels = [
        FieldPanel('slug'),
        FieldPanel('display_name'),
        FieldPanel('is_default'),
        InlinePanel('numbers', label="Quick Numbers"),
    ]

    def clean(self):
        """Validate that only one group is set as default."""
        super().clean()
        if self.is_default:
            existing = QuickNumberGroup.objects.filter(is_default=True).exclude(
                pk=self.pk
            )
            if existing.exists():
                from django.core.exceptions import ValidationError

                raise ValidationError(
                    'Another group is already set as default. Please unset that one first.'
                )

    def __str__(self):
        return self.display_name or self.slug or f"Quick Numbers Group {self.pk}"

    class Meta:
        verbose_name = "Quick Numbers Group"
        verbose_name_plural = "Quick Numbers Groups"


# Cache invalidation signals for Quick Numbers
@receiver(post_save, sender=QuickNumberGroup)
@receiver(post_delete, sender=QuickNumberGroup)
@receiver(post_save, sender=QuickNumber)
@receiver(post_delete, sender=QuickNumber)
def invalidate_quick_nums_cache(sender, **kwargs):
    """Invalidate quick numbers cache when data changes."""
    cache.delete('quick_nums_dict')
