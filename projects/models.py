from django.db import models
from wagtail.core.models import Page
from base.models import BasePage
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.search import index
from django.utils import timezone

class ProjectPage(BasePage):
    """
    Model for project pages.
    """
    # Choices for status
    ACTIVE = 'active'
    PENDING = 'pending'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    DISCUSSION = 'discussion'

    # Choices for size
    SMALL = 'small'
    MEDIUM = 'medium'
    LARGE = 'large'

    STATUS_CHOICES = (
        (ACTIVE, 'Active'),
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
        (DISCUSSION, 'Discussion'),
    )

    SIZE_CHOICES = (
        (SMALL, 'Small'),
        (MEDIUM, 'Medium'),
        (LARGE, 'Large'),
    )


    description = models.TextField(null=False, blank=False)
    requestor = models.CharField(max_length=255, blank=False)
    status = models.CharField(max_length=55,
        choices=STATUS_CHOICES,
        default=ACTIVE)
    size = models.CharField(max_length=55,
        choices=SIZE_CHOICES,
        default=SMALL)
    staff = models.CharField(max_length=255, blank=True)
    date_added_to_list = models.DateField(default=timezone.now)
    completion = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    subpage_types = ['public.StandardPage']

    content_panels = Page.content_panels + [
        FieldPanel('description'),
        FieldPanel('requestor'),
        FieldPanel('status'),
        FieldPanel('size'),
        FieldPanel('staff'),
        FieldPanel('date_added_to_list'),
        FieldPanel('completion'),
        FieldPanel('notes'),
    ] + BasePage.content_panels

    search_fields = BasePage.search_fields + [
        index.SearchField('description'),
        index.SearchField('requestor'),
        index.SearchField('status'),
        index.SearchField('size'),
        index.SearchField('staff'),
        index.SearchField('notes'),
    ]


class ProjectIndexPage(BasePage):
    """
    Homepage for projects.
    """
    subpage_types = ['projects.ProjectPage']

    search_fields = BasePage.search_fields 
