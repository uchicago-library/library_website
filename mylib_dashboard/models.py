from urllib.parse import quote

from django.conf import settings
from django.db import models
from wagtail.admin.panels import FieldPanel, HelpPanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtailcache.cache import WagtailCacheMixin

from mylib_dashboard.utils import get_current_cnetid
from public.models import PublicBasePage


class MyLibDashboardPage(WagtailCacheMixin, PublicBasePage):
    """
    A patron dashboard page that displays account information from
    FOLIO, ILLiad, and LibCal. Content is rendered via React and
    populated from API endpoints.
    """

    # Rendered state depends on the viewer's Shibboleth session. Force
    # Cache-Control: private so wagtailcache won't serve one user's shell
    # (login gate or dashboard) to another.
    cache_control = "private"

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

    # Per-card empty-state messages. Shown when the user has no items in the
    # corresponding category. Rich text so editors can include links.
    EMPTY_STATE_FEATURES = ["bold", "italic", "link"]
    EMPTY_STATE_HELP = (
        "Message shown in this card when the user has no items in this category."
    )

    empty_state_non_renewable_loans = RichTextField(
        blank=True,
        default="No non-renewable loans",
        help_text=EMPTY_STATE_HELP,
        features=EMPTY_STATE_FEATURES,
    )
    empty_state_standard_loans = RichTextField(
        blank=True,
        default="No standard loans",
        help_text=EMPTY_STATE_HELP,
        features=EMPTY_STATE_FEATURES,
    )
    empty_state_pickups = RichTextField(
        blank=True,
        default="No items available for pickup",
        help_text=EMPTY_STATE_HELP,
        features=EMPTY_STATE_FEATURES,
    )
    empty_state_downloads = RichTextField(
        blank=True,
        default="No downloads available",
        help_text=EMPTY_STATE_HELP,
        features=EMPTY_STATE_FEATURES,
    )
    empty_state_ill_in_process = RichTextField(
        blank=True,
        default="No ILL requests in process",
        help_text=EMPTY_STATE_HELP,
        features=EMPTY_STATE_FEATURES,
    )
    empty_state_scan_deliver = RichTextField(
        blank=True,
        default="No scan requests in process",
        help_text=EMPTY_STATE_HELP,
        features=EMPTY_STATE_FEATURES,
    )
    empty_state_paging_requests = RichTextField(
        blank=True,
        default="No paging requests in process",
        help_text=EMPTY_STATE_HELP,
        features=EMPTY_STATE_FEATURES,
    )
    empty_state_room_reservations = RichTextField(
        blank=True,
        default="No upcoming room reservations",
        help_text=EMPTY_STATE_HELP,
        features=EMPTY_STATE_FEATURES,
    )
    empty_state_appointments = RichTextField(
        blank=True,
        default="No upcoming appointments",
        help_text=EMPTY_STATE_HELP,
        features=EMPTY_STATE_FEATURES,
    )
    empty_state_material_requests = RichTextField(
        blank=True,
        default="No material requests",
        help_text=EMPTY_STATE_HELP,
        features=EMPTY_STATE_FEATURES,
    )
    empty_state_reading_room_reservations = RichTextField(
        blank=True,
        default="No upcoming reading room reservations",
        help_text=EMPTY_STATE_HELP,
        features=EMPTY_STATE_FEATURES,
    )

    subpage_types = []

    content_panels = (
        Page.content_panels
        + [
            FieldPanel("auto_renewal_notice"),
            FieldPanel("max_items_per_card"),
            FieldPanel("catalog_account_url"),
            FieldPanel("accounts_faq_url"),
            MultiFieldPanel(
                [
                    FieldPanel("empty_state_non_renewable_loans"),
                    FieldPanel("empty_state_standard_loans"),
                    FieldPanel("empty_state_pickups"),
                    FieldPanel("empty_state_downloads"),
                    FieldPanel("empty_state_ill_in_process"),
                    FieldPanel("empty_state_scan_deliver"),
                    FieldPanel("empty_state_paging_requests"),
                    FieldPanel("empty_state_room_reservations"),
                    FieldPanel("empty_state_appointments"),
                    FieldPanel("empty_state_material_requests"),
                    FieldPanel("empty_state_reading_room_reservations"),
                ],
                heading="Empty State Messages",
                classname="collapsible collapsed",
            ),
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

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["illiad_web_url"] = getattr(settings, "ILLIAD_WEB_BASE_URL", "")
        context["libcal_web_url"] = getattr(settings, "LIBCAL_WEB_URL", "")
        context["is_authenticated"] = bool(get_current_cnetid(request))
        if not context["is_authenticated"]:
            context["shibboleth_login_url"] = "/Shibboleth.sso/Login?target=" + quote(
                request.build_absolute_uri(), safe=""
            )
        return context

    def get_template(self, request, *args, **kwargs):
        if get_current_cnetid(request):
            return "mylib_dashboard/my_lib_dashboard_page.html"
        return "mylib_dashboard/my_lib_dashboard_login.html"

    class Meta:
        verbose_name = "MyLib Dashboard Page"
        verbose_name_plural = "MyLib Dashboard Pages"
