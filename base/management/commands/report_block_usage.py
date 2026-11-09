import csv
import json
from collections import defaultdict

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db.models import TextField
from django.db.models.functions import Cast
from django.urls import reverse
from wagtail.blocks import ListBlock, StreamBlock, StructBlock
from wagtail.fields import StreamField
from wagtail.models import Page

UNDEFINED = "not defined"


def stream_fields(model):
    return [f for f in model._meta.get_fields() if isinstance(f, StreamField)]


def defined_blocks(block, found, seen=None):
    """
    Add (name, class name) for every block an editor can pick in a stream,
    at any depth, to found. The fields of a StructBlock and the items of a
    ListBlock aren't picked by editors, so they don't count; streams nested
    inside them do.
    """
    seen = seen if seen is not None else set()
    if id(block) in seen:
        return
    seen.add(id(block))
    if isinstance(block, StreamBlock):
        for name, child in block.child_blocks.items():
            found.add((name, type(child).__name__))
            defined_blocks(child, found, seen)
    elif isinstance(block, StructBlock):
        for child in block.child_blocks.values():
            defined_blocks(child, found, seen)
    elif isinstance(block, ListBlock):
        defined_blocks(block.child_block, found, seen)


def used_blocks(block, raw, found):
    """
    Add (name, class name) for every stream item in raw, the stored JSON of
    block, at any depth. Items whose type the code no longer defines, such as
    retired blocks still held in the database, are added with UNDEFINED.
    """
    if not raw:
        return
    if isinstance(block, StreamBlock):
        for item in raw:
            if not isinstance(item, dict):
                continue
            name = item.get("type")
            child = block.child_blocks.get(name)
            if child is None:
                found.add((name, UNDEFINED))
                continue
            found.add((name, type(child).__name__))
            used_blocks(child, item.get("value"), found)
    elif isinstance(block, StructBlock) and isinstance(raw, dict):
        for name, child in block.child_blocks.items():
            used_blocks(child, raw.get(name), found)
    elif isinstance(block, ListBlock) and isinstance(raw, list):
        for item in raw:
            # Lists saved since Wagtail 2.16 wrap each item as {"type": "item", ...}
            if (
                isinstance(item, dict)
                and item.get("type") == "item"
                and "value" in item
            ):
                item = item["value"]
            used_blocks(block.child_block, item, found)


def column_titles(keys):
    """
    A block's name, with its class where two blocks share a name, and marked
    when the code no longer defines it.
    """
    names = defaultdict(int)
    for name, _ in keys:
        names[name] += 1
    return {
        key: (
            "{} ({})".format(*key)
            if names[key[0]] > 1 or key[1] == UNDEFINED
            else key[0]
        )
        for key in keys
    }


class Command(BaseCommand):
    """
    Report which StreamField blocks each page type uses, to audit blocks
    before retiring, updating or migrating them.

    Rows are page types and columns are block types, counted at any depth
    (blocks inside columns and other blocks included). Each cell is the
    number of pages of that type using that block at least once. The last two
    rows give the number of pages using each block across all types, and the
    URL of the most recently published of them. Blocks the code defines but
    no page uses get a count of 0; blocks still stored but no longer defined
    are marked "not defined".

    Usage:
        python manage.py report_block_usage > block_usage.csv
        python manage.py report_block_usage --all > block_usage.csv
    """

    help = "CSV of the number of pages of each type using each StreamField block."

    def add_arguments(self, parser):
        parser.add_argument(
            "--all",
            action="store_true",
            help="Include draft and unpublished pages, not only live ones.",
        )

    def handle(self, *args, **options):
        counts = defaultdict(lambda: defaultdict(int))  # page type -> block -> n
        totals = defaultdict(int)  # block -> n
        latest = {}  # block -> (timestamp, page id)
        blocks = set()
        page_types = []

        for model in apps.get_models():
            if not issubclass(model, Page) or model._meta.abstract:
                continue
            fields = stream_fields(model)
            if not fields:
                continue
            page_type = model.__name__
            page_types.append(page_type)
            for field in fields:
                defined_blocks(field.stream_block, blocks)

            # Only pages of this exact type, so a subclass isn't counted twice.
            pages = model.objects.filter(
                content_type=ContentType.objects.get_for_model(model),
                alias_of__isnull=True,
            )
            if not options["all"]:
                pages = pages.live()
            # Read the stored JSON as text: loading the field through Wagtail
            # would silently drop block types the code no longer defines.
            pages = pages.only(
                "id", "last_published_at", "latest_revision_created_at"
            ).annotate(
                **{
                    "raw_" + f.attname: Cast(f.attname, output_field=TextField())
                    for f in fields
                }
            )

            for page in pages.iterator(chunk_size=200):
                found = set()
                for field in fields:
                    raw = json.loads(getattr(page, "raw_" + field.attname) or "[]")
                    used_blocks(field.stream_block, raw, found)
                updated = page.last_published_at or page.latest_revision_created_at
                for key in found:
                    counts[page_type][key] += 1
                    totals[key] += 1
                    if updated and (key not in latest or updated > latest[key][0]):
                        latest[key] = (updated, page.id)
                blocks |= found

        columns = sorted(blocks, key=lambda key: (-totals[key], key))
        titles = column_titles(columns)

        writer = csv.writer(self.stdout)
        writer.writerow(["Page type"] + [titles[key] for key in columns])
        for page_type in sorted(page_types):
            writer.writerow([page_type] + [counts[page_type][key] for key in columns])
        writer.writerow(["All pages"] + [totals[key] for key in columns])
        writer.writerow(
            ["Most recently published"]
            + [
                self.page_url(latest[key][1]) if key in latest else ""
                for key in columns
            ]
        )

    def page_url(self, page_id):
        page = Page.objects.get(id=page_id)
        return page.full_url or reverse("wagtailadmin_pages:edit", args=[page_id])
