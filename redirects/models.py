from base.models import BasePage, LinkFields, PublicBasePage
from django.db import models
from django.shortcuts import redirect
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, PageChooserPanel
from wagtail.models import Page


class RedirectPage(PublicBasePage, LinkFields):
    """
    Page object for setting up redirects that need to
    appear in the sidebar in a given section of the site.
    """
    subpage_types = []

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                PageChooserPanel('link_page'),
                FieldPanel('link_external'),
                FieldPanel('link_document'),
            ],
            heading='Redirect to'
        )
    ] + PublicBasePage.content_panels

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

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                PageChooserPanel('link_page'),
                FieldPanel('link_external'),
                FieldPanel('link_document'),
            ],
            heading='Redirect to'
        )
    ] + BasePage.content_panels

    def serve(self, request):
        """
        Override the serve method to create a redirect.
        """
        return redirect(self.link, permanent=True)
