from django.db import models
from wagtail.wagtailcore.models import Page
from base.models import PublicBasePage, DefaultBodyFields, ContactFields
from wagtail.wagtailsearch import index
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel, PageChooserPanel, StreamFieldPanel

class AskPage(PublicBasePage, ContactFields):
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
        MultiFieldPanel(
            [
                PageChooserPanel('link_page'),
                FieldPanel('link_external'),
            ],
            heading='Contact Form'
        ),
        FieldPanel('email'),
        FieldPanel('phone_number'), 
        StreamFieldPanel('body'),
    ] + PublicBasePage.content_panels

    search_fields = PublicBasePage.search_fields + (
        index.SearchField('ask_widget_name'),
        index.SearchField('reference_resources'),
        index.SearchField('body'),
        index.SearchField('email'),
        index.SearchField('email_label'),
        index.SearchField('phone_number'),
        index.SearchField('body'),
    )
