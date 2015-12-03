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
    author = models.ForeignKey(
        'staff.StaffPage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='news_stories'
    )
    story_date = models.DateField(default=timezone.now)
    sticky_until = models.DateField(blank=True, null=True)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+')
    body = StreamField(DefaultBodyFields(), blank=False, null=False)

    content_panels = Page.content_panels + [ 
        FieldPanel('excerpt'),
        FieldPanel('author'),
        FieldPanel('story_date'),
        FieldPanel('sticky_until'),
        ImageChooserPanel('image'),
        StreamFieldPanel('body'),
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

    def get_context(self, request):
        context = super(NewsIndexPage, self).get_context(request)
        # need to add order_by('story_date')
        news_pages = sorted(self.get_children().live())
        # need to add author name and url, and excerpt.
        context['news_pages'] = list(map(lambda s: { 'story_date': s.specific_class().story_date.strftime('%B %d').replace(' 0', ' '), 'author_title': 'Author', 'author_url': '/', 'excerpt': 'excerpt.', 'title': s.title, 'url': s.url }, news_pages))
        return context
