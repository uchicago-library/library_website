import csv
import io

from django.core.management.base import BaseCommand
from wagtail.models import Page


class Command(BaseCommand):
    """
    Report pages containing legacy video embeds that need title attributes.

    This command identifies pages with the old 'video' block (EmbedBlock) that
    lacks title attributes for ADA compliance. These should be converted to
    'video_with_title' (VideoEmbedBlock).

    Related to GitHub issues #333, #900 - Video embed iframe lacks title attribute

    Example:
        python manage.py report_legacy_video_embeds > legacy_videos.csv
    """

    help = 'Report pages with legacy video embeds that need ADA-compliant titles'

    def handle(self, *args, **options):
        """
        Find all pages with legacy video embeds and report them.
        """
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                'Page URL',
                'Page Title',
                'Page Type',
                'Field Name',
                'Video Count',
                'Video HTML',
            ]
        )

        total_pages = 0
        total_videos = 0

        # Iterate through all pages
        for page in Page.objects.live():
            try:
                specific_page = page.specific
            except Exception:
                continue

            # Check StreamFields that might contain video blocks
            for field_name in [
                'body',
                'intro',
                'bio',
                'collecting_statement',
                'full_description',
            ]:
                if not hasattr(specific_page, field_name):
                    continue

                stream_field = getattr(specific_page, field_name)
                if not stream_field:
                    continue

                # Find legacy video blocks
                legacy_videos = []
                try:
                    for block in stream_field:
                        if block.block_type == 'video':
                            # This is the legacy EmbedBlock
                            legacy_videos.append(str(block.value))
                except Exception:
                    continue

                if legacy_videos:
                    total_pages += 1
                    total_videos += len(legacy_videos)

                    video_html = ' | '.join(legacy_videos)
                    writer.writerow(
                        [
                            page.url,
                            page.title,
                            specific_page.__class__.__name__,
                            field_name,
                            len(legacy_videos),
                            video_html,
                        ]
                    )

        # Print summary to stderr so it doesn't interfere with CSV output
        summary = f"\nSummary: Found {total_videos} legacy video embed(s) across {total_pages} page(s)\n"
        summary += "These videos lack title attributes for ADA compliance.\n"
        summary += "Editors should replace 'video' blocks with 'video_with_title' blocks and add descriptive titles.\n"

        self.stderr.write(self.style.SUCCESS(summary))

        return output.getvalue()
