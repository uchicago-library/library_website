from django.db import models
from django.shortcuts import redirect
from wagtail.core.models import Page
from wagtail.admin.edit_handlers import FieldPanel, FieldRowPanel, MultiFieldPanel, PageChooserPanel
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.search import index
from base.models import PublicBasePage, LinkFields

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
                DocumentChooserPanel('link_document'),
            ],
            heading='Redirect to'
        )
    ] + PublicBasePage.content_panels

    search_fields = PublicBasePage.search_fields + [
        index.SearchField('link_page', partial_match=True),
        index.SearchField('link_external', partial_match=True),
    ]

    def serve(self, request):
        """
        Override the serve method to create a redirect. 
        """
        return redirect(self.link, permanent=True)
