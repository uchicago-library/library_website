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

    def get_context(self, request):
        context = super(NewsPage, self).get_context(request)

        details = get_story_summary(self)
        context['story_date'] = details['story_date']
        try:
            context['author_title'] = details['author_title']
        except:
            context['author_title'] = ''
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

    search_fields = BasePage.search_fields + [
        index.SearchField('intro'),
    ]

    def get_context(self, request):
        context = super(NewsIndexPage, self).get_context(request)
        # need to add order_by('story_date')

        sticky_pages = get_stories(sticky=True)
        news_pages = get_stories()

        page = int(request.GET.get('page', 1))
        news_pages = get_stories_by_page(page)

        prev_link = None 
        if page > 1:
            prev_link = "%s?page=%s" % (request.path, str(page - 1))
        next_link = None
        if get_story_count() > page * get_stories_by_page.page_length:
            next_link = "%s?page=%s" % (request.path, str(page + 1))

        context['sticky_pages'] = sticky_pages
        context['news_pages'] = news_pages
        context['prev_link'] = prev_link
        context['next_link'] = next_link
        return context

def get_stories(sticky=False):
    pages = []
    if sticky:
        for page in NewsPage.objects.live():
            # skip stories that are in the future. 
            if page.story_date > datetime.date(datetime.now()):
                continue
            # skip stories that do not have a "sticky until" date.
            if page.sticky_until == None:
                continue
            # skip sticky stories that have 'expired'.
            if page.sticky_until and datetime.date(datetime.now()) > page.sticky_until:
                continue
            pages.append(get_story_summary(page))
    else:
        for page in NewsPage.objects.live():
            # skip stories that are in the future. 
            if page.story_date > datetime.date(datetime.now()):
                continue
            # skip pages that are still sticky. 
            # pages that have a sticky_until set to None or a date in the past fall through.
            if page.sticky_until and datetime.date(datetime.now()) <= page.sticky_until:
                continue
            pages.append(get_story_summary(page))

    return sorted(pages, key=lambda p: (p['story_date_sort'], p['latest_revision_created_at']), reverse=True)

def get_stories_by_page(page=1, sticky=False):
    get_stories_by_page.page_length = 10

    stories = get_stories(sticky)
    start_page = (page - 1) * get_stories_by_page.page_length
    end_page = start_page + get_stories_by_page.page_length
    return stories[start_page:end_page]

def get_story_count(sticky=False):
    return len(get_stories(sticky))

def get_story_summary(news_page):
    def simplify_text(s):
        # strip out every HTML tag except opening and closing <a> tags. 
        s = re.sub(r"<(?!\/?a(?=>|\s.*>))\/?.*?>", " ", s)
        s = re.sub(r"\s+", " ", s)
        return s.strip()

    # get the first num_words (e.g. 50) words. 
    # don't allow unclosed anchor tags through.
    def get_excerpt_safely(words, num_words):
        excerpt_words = words[:num_words]
        opening_anchor_tag_count = sum('<a' not in word for word in excerpt_words)
        closing_anchor_tag_count = sum('</a>' not in word for word in excerpt_words)
        if opening_anchor_tag_count != closing_anchor_tag_count:
            while True:
                last_word = excerpt_words.pop()
                if not last_word:
                    break
                if '<a' in last_word:
                    break
        return ' '.join(excerpt_words)
    
    day = int(news_page.story_date.strftime('%d'))
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]

    if news_page.author:
        author_title = news_page.author.title
        author_url = news_page.author.url
    else:
        try:
            cnetid = news_page.owner.username
            author_title = StaffPage.objects.filter(cnetid=cnetid)[0].title
            author_url = StaffPage.objects.filter(cnetid=cnetid)[0].url
        except:
            author_title = ''
            author_url = ''

    simplified_text = simplify_text(news_page.excerpt)
    if simplified_text:
        words = simplified_text.split(" ")
        excerpt = get_excerpt_safely(words, 50)
        read_more = True
    else:
        simplified_text = simplify_text(" ".join([s.render() for s in news_page.body]))
        words = simplified_text.split(" ")
        excerpt = get_excerpt_safely(words, 50)

        if len(words) > 50:
            excerpt = excerpt + "..."
            read_more = True
        else:
            read_more = False

    return {
        'story_date_sort': news_page.story_date,
        'story_date': news_page.story_date.strftime('%B %d').replace(' 0', ' ') + suffix,
        'latest_revision_created_at': news_page.latest_revision_created_at,
        'author_title': author_title,
        'author_url': author_url,
        'excerpt': excerpt,
        'read_more': read_more,
        'title': news_page.title,
        'url': news_page.url,
        'body': news_page.body,
        'thumbnail': news_page.thumbnail,
        'page_alt' : news_page.alt_text
    }

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
