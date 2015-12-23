from datetime import datetime

from django.db import models
from django.db.models.fields import TextField
from django.utils import timezone

from base.models import BasePage, DefaultBodyFields
from staff.models import StaffPage

from wagtail.wagtailadmin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailcore.models import Page
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel

import re

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
    thumbnail = models.ForeignKey(
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
        ImageChooserPanel('thumbnail'),
        StreamFieldPanel('body'),
    ] + BasePage.content_panels

    def get_context(self, request):
        context = super(NewsPage, self).get_context(request)

        details = get_story_summary(self)
        context['story_date'] = details['story_date']
        context['author_title'] = details['author_title']
        context['author_url'] = details['author_url']
        context['thumbnail'] = details['thumbnail']

        return context

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

        sticky_pages = get_stories(sticky=True)
        if sticky_pages:
            sticky_pages = [sticky_pages.pop(0)]

        news_pages = get_stories()

        context['sticky_pages'] = sticky_pages
        context['news_pages'] = news_pages
        return context

def get_stories(sticky=False):
    pages = []
    if sticky:
        for page in NewsPage.objects.live().exclude(sticky_until=None):
            # skip stories that are in the future. 
            if page.story_date > datetime.date(datetime.now()):
                continue
            # skip sticky stories that have 'expired'.
            if page.sticky_until and datetime.date(datetime.now()) > page.sticky_until:
                continue
            pages.append(get_story_summary(page))
    else:
        for page in NewsPage.objects.live().filter(sticky_until=None):
            # skip stories that are in the future. 
            if page.story_date > datetime.date(datetime.now()):
                continue
            pages.append(get_story_summary(page))

    return sorted(pages, key=lambda p: p['story_date_sort'], reverse=True)

def get_story_summary(news_page):
    def simplify_text(s):
        # strip out every HTML tag except opening and closing <a> tags. 
        s = re.sub(r"<(?!\/?a(?=>|\s.*>))\/?.*?>", " ", s)
        s = re.sub(r"\s+", " ", s)
        return s.strip()
    
    day = int(news_page.story_date.strftime('%d'))
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]

    if news_page.author:
        author_title = news_page.author.title
        author_url = news_page.author.url
    else:
        cnetid = news_page.owner.username
        author_title = StaffPage.objects.get(cnetid=cnetid).title
        author_url = StaffPage.objects.get(cnetid=cnetid).url

    simplified_text = simplify_text(news_page.excerpt)
    if not simplified_text:
        simplified_text = simplify_text(" ".join([s.render() for s in news_page.body]))

    words = simplified_text.split(" ")
    excerpt = " ".join(words[:50])

    if len(words) > 50:
        excerpt = excerpt + "..."
        read_more = True
    else:
        read_more = False

    return {
        'story_date_sort': news_page.story_date,
        'story_date': news_page.story_date.strftime('%B %d').replace(' 0', ' ') + suffix,
        'author_title': author_title,
        'author_url': author_url,
        'excerpt': excerpt,
        'read_more': read_more,
        'title': news_page.title,
        'url': news_page.url,
        'body': news_page.body,
        'thumbnail': news_page.thumbnail
    }
