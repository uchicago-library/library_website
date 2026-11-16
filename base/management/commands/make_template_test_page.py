"""
Create or update a draft standard page that shows every sidebar widget,
every widget below the content and one of each body block, for checking
templates as they move to the design system (#1109).

The page is only ever saved as a draft, hidden from menus and search
engines, so running this against a production database publishes nothing.
Open it from the Wagtail admin with "View draft" (preview). Running the
command again updates the same page with a new draft revision.

Widgets and blocks that need an image, a staff page, a collection page or a
reusable content snippet use the first one in the database, and are left out
when there is none.

    ./manage.py make_template_test_page [--parent PAGE_ID]
"""

from django.core.management.base import BaseCommand, CommandError
from wagtail.images import get_image_model
from wagtail.models import Page, Site

from lib_collections.models import CollectionPage
from public.models import (
    StandardPage,
    StandardPageCarouselItem,
    StandardPageIconLinkItem,
    StandardPageSidebarReusableContent,
)
from reusable_content.models import ReusableContent
from staff.models import StaffPage
from units.models import UnitPage
from units.utils import get_default_unit

SLUG = "template-test-page"
LIBRARY = "https://www.lib.uchicago.edu/"
TEXT = (
    "<p>A paragraph with <a href='https://www.lib.uchicago.edu/'>a link</a>, "
    "<b>bold</b> and <i>italic</i> text, long enough to wrap onto a second "
    "line in a narrow column.</p>"
)


def default_unit():
    """The site's default unit, or the first live unit where it is missing."""
    try:
        return get_default_unit()
    except IndexError:
        return first_live(UnitPage)


def first_live(model):
    return model.objects.live().first()


def image_blocks(image):
    """Blocks that need an image, or none when the database has no images."""
    if not image:
        return []
    solo = {
        "image": image.id,
        "citation": "<p>Citation</p>",
        "caption": "<p>Caption for a solo image.</p>",
        "alt_text": "Solo image",
    }
    blocks = [{"type": "h2", "value": "Images"}]
    for alignment in ["fullwidth", "pull-left", "pull-right"]:
        blocks += [
            {
                "type": "image",
                "value": {
                    "image": image.id,
                    "title": f"Image block ({alignment})",
                    "citation": "Citation",
                    "caption": "Caption for an image block.",
                    "alt_text": f"Image block, {alignment}",
                    "alignment": alignment,
                    "source": LIBRARY,
                    "lightbox": False,
                },
            },
            {"type": "paragraph", "value": {"paragraph": TEXT}},
            {"type": "clear", "value": {}},
        ]
    blocks += [
        {"type": "solo_image", "value": solo},
        {"type": "duo_image", "value": {"image_one": solo, "image_two": solo}},
        {
            "type": "image_link",
            "value": {
                "image": image.id,
                "alt_text": "Image link",
                "icon": "",
                "link_text": "Image link with an image",
                "link_external": LIBRARY,
                "link_page": None,
                "link_document": None,
            },
        },
    ]
    return blocks


def body(image, staff, snippet):
    blocks = [
        {"type": "paragraph", "value": {"paragraph": TEXT}},
        {"type": "h2", "value": "Heading 2"},
        {"type": "h3", "value": "Heading 3"},
        {"type": "h4", "value": "Heading 4"},
        {"type": "h5", "value": "Heading 5"},
        {
            "type": "columns_block",
            "value": [
                {"type": "new_column", "value": f"<p>Column {n}.</p>{TEXT}"}
                for n in (1, 2, 3)
            ],
        },
        {
            "type": "blockquote",
            "value": {"quote": "A block quote.", "attribution": "Its author"},
        },
        {"type": "pullquote", "value": {"quote": "<p>A pull quote.</p>"}},
        {"type": "h2", "value": "Links"},
    ]
    for button_type in ["btn-primary", "btn-default", "btn-reserve"]:
        blocks.append(
            {
                "type": "button",
                "value": {
                    "button_type": button_type,
                    "button_text": f"Button ({button_type})",
                    "link_external": LIBRARY,
                    "link_page": None,
                    "link_document": None,
                },
            }
        )
    blocks += [
        {
            "type": "image_link",
            "value": {
                "image": None,
                "alt_text": "",
                "icon": "fa-book",
                "link_text": "Image link with an icon",
                "link_external": LIBRARY,
                "link_page": None,
                "link_document": None,
            },
        },
        {
            "type": "video_with_title",
            "value": {
                "url": "https://www.youtube.com/watch?v=jNQXAC9IVRw",
                "title": "Video with a title",
            },
        },
    ]
    blocks += image_blocks(image)
    blocks += [
        {"type": "h2", "value": "Layout and data"},
        {
            "type": "table",
            "value": {
                "data": [["Day", "Opens", "Closes"], ["Monday", "8am", "10pm"]],
                "first_row_is_table_header": True,
                "first_col_is_header": False,
                "table_caption": "Table block",
            },
        },
        {
            "type": "agenda_item",
            "value": {
                "start_time": "09:00",
                "end_time": "10:00",
                "session_title": "Agenda item",
                "event": [
                    {
                        "title": "Opening session",
                        "presenters": "A presenter",
                        "room_number": "Room 122",
                        "description": "<p>What the session covers.</p>",
                    }
                ],
            },
        },
        {"type": "code", "value": {"language": "html", "code": "<p>Code</p>"}},
        {
            "type": "mermaid",
            "value": {
                "source": "graph LR\n  A[Request] --> B[Pickup]",
                "description": "A request goes to pickup.",
                "title": "Mermaid diagram",
            },
        },
        {
            "type": "page_listing",
            "value": {"heading": "Page listing", "root_page": None, "depth": "1"},
        },
        {"type": "markdown", "value": "A **Markdown** block with a [link](/)."},
        {"type": "html", "value": "<p>A raw HTML block.</p>"},
        {"type": "anchor_target", "value": {"anchor_id_name": "anchor-target"}},
    ]
    if staff:
        blocks.append(
            {
                "type": "staff_listing",
                "value": {
                    "staff_listing": [staff.id],
                    "show_photos": True,
                    "show_contact_info": True,
                    "show_subject_specialties": True,
                },
            }
        )
    if snippet:
        blocks.append({"type": "reusable_content", "value": {"content": snippet.id}})
    return blocks


class Command(BaseCommand):
    help = (
        "Create or update a draft standard page with every widget and block, "
        "for checking templates. Never publishes."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--parent",
            type=int,
            help="Id of the parent page. Defaults to the default site's root page.",
        )

    def handle(self, *args, **options):
        parent = self.get_parent(options["parent"])
        image = get_image_model().objects.first()
        staff = first_live(StaffPage)
        snippet = ReusableContent.objects.first()

        page = StandardPage.objects.child_of(parent).filter(
            slug=SLUG
        ).first() or StandardPage(slug=SLUG, live=False)
        created = page.pk is None
        if page.live:
            raise CommandError(
                f"{page.url_path} is published. Unpublish it first: this "
                "command only saves drafts."
            )

        self.fill(page, image, staff, snippet)
        if created:
            parent.add_child(instance=page)
        page.save_revision(log_action=True)

        self.stdout.write(
            f"{'Created' if created else 'Updated'} draft page {page.id}: "
            f"preview it at /admin/pages/{page.id}/view_draft/"
        )
        for name, found in [
            ("image", image),
            ("staff page", staff),
            ("reusable content", snippet),
        ]:
            if not found:
                self.stdout.write(
                    f"No {name} in the database: its blocks are left out."
                )

    def get_parent(self, parent_id):
        if parent_id:
            try:
                return Page.objects.get(id=parent_id)
            except Page.DoesNotExist:
                raise CommandError(f"No page with id {parent_id}.")
        site = Site.objects.filter(is_default_site=True).first()
        if not site:
            raise CommandError("No default site. Pass --parent.")
        return site.root_page

    def fill(self, page, image, staff, snippet):
        page.title = "Template test page"
        page.show_in_menus = False
        page.exclude_from_search_engines = True
        page.search_description = "Every widget and block, for checking templates."
        page.unit = default_unit()
        page.page_maintainer = page.editor = page.content_specialist = staff

        page.body = body(image, staff, snippet)

        # Banner and carousel
        if image:
            page.banner_image = page.banner_feature = image
            page.banner_title = "Banner title"
            page.banner_subtitle = "Banner subtitle"
            page.carousel_items = [
                StandardPageCarouselItem(
                    image=image,
                    image_title=f"Carousel item {n}",
                    image_subtitle="Its subtitle",
                    link_external=LIBRARY,
                )
                for n in (1, 2)
            ]

        # Left section navigation
        page.show_sidebar = True

        # Search widget (standard_page.html, not the base)
        page.enable_search_widget = True

        # Right sidebar
        page.quicklinks_title = "Quick links"
        page.quicklinks = "<ul><li><a href='/'>A quick link</a></li></ul>"
        page.view_more_link = LIBRARY
        page.view_more_link_label = "View more"
        page.change_to_callout = True
        page.display_hours_in_right_sidebar = True
        page.widget_title = "Icon links"
        page.icon_link_items = [
            StandardPageIconLinkItem(icon=icon, link_label=label, link_external=LIBRARY)
            for icon, label in [
                ("fa-book", "Books"),
                ("fa-print", "Printing"),
                ("fa-exclamation-triangle", "An old Font Awesome name"),
            ]
        ]
        page.more_icons_link = LIBRARY
        page.more_icons_link_label = "More icon links"
        page.enable_find_spaces = True
        page.book_a_room_link = "https://rooms.lib.uchicago.edu/"
        page.events_feed_url = "https://events.uchicago.edu/"
        page.collection_page = first_live(CollectionPage)
        page.twitter_page = "https://twitter.com/UChicagoLibrary"
        page.facebook_page = "https://www.facebook.com/UChicagoLibrary"
        page.instagram_page = "https://www.instagram.com/uchicagolibrary/"
        page.youtube_page = "https://www.youtube.com/user/UChicagoLibrary"
        page.blog_page = LIBRARY + "about/news/"
        page.hashtag = "#UChicagoLibrary"
        page.hashtag_page = "https://twitter.com/hashtag/UChicagoLibrary"
        page.reusable_content = (
            [StandardPageSidebarReusableContent(content=snippet)] if snippet else []
        )

        # Below the content
        page.rich_text_heading = "Rich text widget"
        page.rich_text = TEXT
        page.rich_text_link_text = "View all"
        page.rich_text_external_link = LIBRARY
        page.news_feed_source = "library_kiosk"
        page.expert_link = (
            "/about/directory/?view=staff&subject=All+Subject+Specialists"
        )
        page.featured_library_expert_fallback = (
            [
                {
                    "type": "person",
                    "value": {
                        "library_expert": staff.id,
                        "libguides": [
                            {
                                "link_text": "A research guide",
                                "link_external": "https://guides.lib.uchicago.edu/",
                                "link_page": None,
                            }
                        ],
                    },
                }
            ]
            if staff
            else []
        )
