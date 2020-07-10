from datetime import datetime

from django.core.paginator import Paginator
from django.db import models
from django.db.models.fields import TextField
from django.utils import timezone

from base.models import BasePage, PublicBasePage, DefaultBodyFields
from staff.models import StaffPage

from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel, MultiFieldPanel
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.snippets.models import register_snippet

import re

class NewsPage(BasePage):
    """
    News story content type used on intranet pages.
    """
    excerpt = RichTextField(blank=True, null=True, help_text='Shown on the News feed. Populated automatically from “Body” if left empty.')
    author = models.ForeignKey(
        'staff.StaffPage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='news_stories'
    )
    story_date = models.DateField(default=timezone.now, help_text='If you use Settings to publish a future post, put the publish date here. Otherwise, leave today as the story date.')
    sticky_until = models.DateField(blank=True, null=True, help_text='To be used by Admin and HR only.')
    thumbnail = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+')
    alt_text = models.CharField(max_length=100, blank=True)
    body = StreamField(DefaultBodyFields(), blank=False, null=False)

    subpage_types = []

    content_panels = Page.content_panels + [ 
        StreamFieldPanel('body'),
        FieldPanel('author'),
        FieldPanel('story_date'),
        MultiFieldPanel(
            [
                ImageChooserPanel('thumbnail'),
                FieldPanel('alt_text'),
            ],
            heading='Thumbnail',
        ),
        FieldPanel('excerpt'),
    ] + BasePage.content_panels

    promote_panels = BasePage.promote_panels + [
        FieldPanel('sticky_until'),
    ]

    search_fields = PublicBasePage.search_fields + [
        index.SearchField('excerpt'),
        index.SearchField('author'),
        index.SearchField('thumbnail'),
        index.SearchField('body'),
    ]

    @classmethod
    def get_stories(cls, sticky=False, now=None):
        """
	A handy function to efficiently get a list of news stories to display
        on Loop.

        Parameters:
	sticky -- A boolean. If this is set to True, the method will return
		  sticky stories only. Setting this to False returns non-sticky
                  stories only.
	now    -- A datetime.date(), or None. If None, the method will set now
		  to the current date. This parameter is present to make this
                  function easier to test.
 
        Returns:
        A django.core.paginator.Paginator object for Loop news stories. 
        """

        if now == None:
            now = datetime.date(datetime.now())

        stories = cls.objects.filter(
            live=True,
            story_date__lte=now,
        ).order_by(
            '-story_date',
            '-latest_revision_created_at'
        )
        if sticky:
            stories = stories.filter(sticky_until__gte=now)
        else:
            stories = stories.exclude(sticky_until__gte=now)
    
        return Paginator(stories, 10)
 

class NewsIndexPage(BasePage):
    """
    Index page for intranet news stories.
    """
    max_count = 1
    subpage_types = ['news.NewsPage']
    intro = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ] + BasePage.content_panels

    subpage_types = ['news.NewsPage']

    search_fields = BasePage.search_fields + [
        index.SearchField('intro'),
    ]


@register_snippet
class NewsEmailAddition(models.Model, index.Indexed):
    include_in_email_dated = models.DateField(null=False, blank=False, default=datetime.now, help_text='Emails are send automatically via cron. Only email additions with the appropriate date will be attached to messages.')
    text = RichTextField(help_text='Text to include in emails. This can include internal or external links.')

    panels = [
        FieldPanel('include_in_email_dated'),
        FieldPanel('text')
    ]

    def __str__(self):
        return self.include_in_email_dated.strftime("%B %-d, %Y")
