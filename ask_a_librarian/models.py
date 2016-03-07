from django.db import models
from wagtail.wagtailcore.models import Page
from base.models import PublicBasePage, PhoneNumber, Email, DefaultBodyFields
from wagtail.wagtailsearch import index
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, StreamFieldPanel

class AskPage(PublicBasePage, PhoneNumber, Email):
    """
    Page type for Ask A Librarian pages.
    """

    ask_widget_name = models.CharField(max_length=100, blank=True)
    reference_resources = RichTextField()
    body = StreamField(DefaultBodyFields())

    subpage_types = ['public.StandardPage']

    content_panels = Page.content_panels + [
        FieldPanel('ask_widget_name'),
        FieldPanel('reference_resources'),
        StreamFieldPanel('body'),
    ] + PhoneNumber.content_panels + Email.content_panels \
      + PublicBasePage.content_panels

    search_fields = PublicBasePage.search_fields + (
        index.SearchField('ask_widget_name'),
        index.SearchField('reference_resources'),
        index.SearchField('body'),
        index.SearchField('email'),
        index.SearchField('email_label'),
        index.SearchField('phone_label'),
        index.SearchField('phone_number'),
        index.SearchField('body'),
    )
