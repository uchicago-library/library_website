from base.models import PublicBasePage, DefaultBodyFields
from django.db.models.fields import CharField
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.search import index


class DirBrowsePage(PublicBasePage):
    body = StreamField(
        DefaultBodyFields(),
        blank=True,
        null=True,
        use_json_field=True,
    )
    dir_browse_script_url = CharField(
        max_length=255,
        blank=False)

    search_fields = PublicBasePage.search_fields + [
        index.SearchField('body'),
    ]

    subpage_types = []

    content_panels = Page.content_panels + [
        FieldPanel('body'),
        FieldPanel('dir_browse_script_url')
    ] + PublicBasePage.content_panels
