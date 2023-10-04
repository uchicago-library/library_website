from base.models import BasePage, DefaultBodyFields, LinkFields, PublicBasePage
from django.shortcuts import redirect
from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
    ObjectList,
    PageChooserPanel,
    TabbedInterface,
)
from wagtail.api import APIField
from wagtail.fields import StreamField
from wagtail.models import Page


class RedirectPage(PublicBasePage, LinkFields):
    """
    Page object for setting up redirects that need to
    appear in the sidebar in a given section of the site.
    """

    body = StreamField(
        DefaultBodyFields(),
        blank=True,
        use_json_field=True,
    )

    subpage_types = []

    content_panels = (
        Page.content_panels
        + [
            MultiFieldPanel(
                [
                    PageChooserPanel('link_page'),
                    FieldPanel('link_external'),
                    FieldPanel('link_document'),
                ],
                heading='Redirect to',
            )
        ]
        + PublicBasePage.content_panels
    )

    admin_content_panels = [
        MultiFieldPanel(
            [
                FieldPanel('quicklinks_title'),
                FieldPanel('quicklinks'),
            ],
            heading='Quicklinks',
        ),
        FieldPanel('body'),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading='Content'),
            ObjectList(PublicBasePage.promote_panels, heading='Promote'),
            ObjectList(Page.settings_panels, heading='Settings', classname="settings"),
            ObjectList(admin_content_panels, heading='Admin'),
        ]
    )

    api_fields = PublicBasePage.api_fields + [APIField('body')]

    search_fields = []

    def serve(self, request):
        """
        Override the serve method to create a redirect.
        """
        return redirect(self.link, permanent=True)


class LoopRedirectPage(BasePage, LinkFields):
    """
    Page object for setting up redirects in loop that need to
    appear in the sidebar in a given section of the site.
    """

    subpage_types = []

    content_panels = (
        Page.content_panels
        + [
            MultiFieldPanel(
                [
                    PageChooserPanel('link_page'),
                    FieldPanel('link_external'),
                    FieldPanel('link_document'),
                ],
                heading='Redirect to',
            )
        ]
        + BasePage.content_panels
    )

    search_fields = []

    def serve(self, request):
        """
        Override the serve method to create a redirect.
        """
        return redirect(self.link, permanent=True)
