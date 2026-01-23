from django.db import models
from wagtail.admin.panels import FieldPanel, HelpPanel
from wagtail.fields import RichTextField
from wagtail.models import Page

from public.models import PublicBasePage


class MyLibDashboardPage(PublicBasePage):
    """
    A patron dashboard page that displays account information from
    FOLIO, ILLiad, and LibCal. Content is rendered via React and
    populated from API endpoints.
    """

    auto_renewal_notice = RichTextField(
        blank=True,
        default="<b>Auto-renewal is enabled.</b> Items will be automatically "
        "renewed up to 5 times unless recalled or you have fines over $25.",
        help_text="Dismissible notice shown at top of dashboard. "
        "Leave blank to hide the notice.",
        features=["bold", "italic", "link"],
    )

    max_items_per_card = models.PositiveIntegerField(
        default=0,
        help_text="Maximum items to show per category card before showing "
        "'+X more items'. Set to 0 to show all items.",
    )

    catalog_account_url = models.URLField(
        blank=True,
        default="https://catalog.lib.uchicago.edu/vufind/MyResearch/Home",
        help_text="URL to the library catalog account page (e.g., VuFind My Account).",
    )

    accounts_faq_url = models.URLField(
        blank=True,
        default="https://www.lib.uchicago.edu/borrow/borrowing/my-accounts/",
        help_text="URL to the Accounts FAQ page.",
    )

    subpage_types = []

    content_panels = (
        Page.content_panels
        + [
            FieldPanel("auto_renewal_notice"),
            FieldPanel("max_items_per_card"),
            FieldPanel("catalog_account_url"),
            FieldPanel("accounts_faq_url"),
            HelpPanel(
                heading="About the MyLib Dashboard",
                content="""
                <p>This page displays a patron's library account information including:</p>
                <ul>
                    <li>Checked out items (loans)</li>
                    <li>Items available for pickup (holds)</li>
                    <li>Requests in process</li>
                    <li>Room reservations</li>
                    <li>Fines and account status</li>
                </ul>
                <p>All content is loaded dynamically via the React dashboard application.
                The page inherits the public site header and footer.</p>
                """,
            ),
        ]
        + PublicBasePage.content_panels
    )

    search_fields = PublicBasePage.search_fields

    class Meta:
        verbose_name = "MyLib Dashboard Page"
        verbose_name_plural = "MyLib Dashboard Pages"
