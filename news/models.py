from django.db import models
from django.db.models.fields import TextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailcore.models import Page
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from base.models import DefaultBodyFields
from django.utils import timezone

class NewsPage(Page):
    """
    News story content type used on intranet pages.
    """
    body = StreamField(DefaultBodyFields());
    excerpt = models.TextField(blank=True)
    thumbnail_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+')
    sticky_until = models.DateField(blank=False, default=timezone.now)

    content_panels = Page.content_panels + [ 
        FieldPanel('excerpt'),
        StreamFieldPanel('body'),
        ImageChooserPanel('thumbnail_image'),
        FieldPanel('sticky_until'),
    ] 

class NewsIndexPage(Page):
    """
    Index page for intranet news stories.
    """
    intro = TextField()

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ]

    subpage_types = ['home.NewsPage']
