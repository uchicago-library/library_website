from base.models import DefaultBodyFields

from django.db import models
from django.db.models.fields import TextField
from django.utils import timezone

from base.models import BasePage

from wagtail.wagtailadmin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailcore.models import Page
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from base.models import DefaultBodyFields

class NewsPage(BasePage):
    """
    News story content type used on intranet pages.
    """
    excerpt = RichTextField(blank=True, null=True)
    thumbnail_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+')
    body = StreamField(DefaultBodyFields(), blank=False, null=False)
    publish_on = models.DateField(default=timezone.now)
    sticky_until = models.DateField(blank=True, null=True)

    content_panels = Page.content_panels + [ 
        FieldPanel('excerpt'),
        ImageChooserPanel('thumbnail_image'),
        StreamFieldPanel('body'),
        FieldPanel('publish_on'),
        FieldPanel('sticky_until')
    ] + BasePage.content_panels

class NewsIndexPage(BasePage):
    """
    Index page for intranet news stories.
    """
    intro = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ] + BasePage.content_panels

    subpage_types = ['news.NewsPage']
