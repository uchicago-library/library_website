from base.models import BasePage
from icon_list_boxes.models import IconListCluster
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.search import index


class TOCPage(BasePage):
    """
    Table of Contents Pages for the intranet.
    """
    body = StreamField(
        IconListCluster(),
    )

    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ] + BasePage.content_panels

    subpage_types = [
        'base.IntranetIndexPage', 'base.IntranetPlainPage',
        'intranettocs.TOCPage'
    ]

    search_fields = BasePage.search_fields + [
        index.SearchField('body'),
    ]
