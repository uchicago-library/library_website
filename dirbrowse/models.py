from base.models import PublicBasePage, DefaultBodyFields
from django.db import models
from django.db.models.fields import CharField
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core.fields import StreamField
from wagtail.core.models import Page
from wagtail.search import index

class DirBrowsePage(PublicBasePage):
    body = StreamField(DefaultBodyFields(), blank=True, null=True)
    dir_browse_script_url = CharField(
        max_length=255,
        blank=False)

    search_fields = PublicBasePage.search_fields + [
        index.SearchField('body'),
    ]

    subpage_types = []

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
        FieldPanel('dir_browse_script_url')
    ] + PublicBasePage.content_panels
