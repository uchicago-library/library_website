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

    subpage_types = []

    content_panels = (
        Page.content_panels
        + [
            FieldPanel("auto_renewal_notice"),
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
