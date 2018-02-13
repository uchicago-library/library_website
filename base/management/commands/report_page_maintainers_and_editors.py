# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from wagtail.wagtailcore.models import Page

import csv
import io
import sys

#os.environ['DJANGO_SETTINGS_MODULE'] = 'library_website.settings'

class Command (BaseCommand):
    """
    Produce a report of pages for which a given person is the maintainer,
    editor or content specialist. 

    Example: 
        python manage.py report_page_maintainers_and_editors cnetid
    """

    def add_arguments(self, parser):
        """
        Add required positional options and optional
        named arguments.
        """
        # optional argument.
        parser.add_argument('cnetid', nargs='?', type=str)

    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement this 
        method. It may return a Unicode string which will be printed to 
        stdout. More: https://docs.djangoproject.com/en/1.8/howto/custom
        -management-commands/#django.core.management.BaseCommand.handle
        """

        cnetid = options['cnetid']

        records = []
        records.append(('URL', 'Page Title', 'Last Modified', 'Last Reviewed', 'Page Maintainer CNetID', 'Page Maintainer', 'Editor CNetID', 'Editor', 'Content Specialist CNetID', 'Content Specialist'))
        for p in Page.objects.all():
            # Skip pages that aren't live. 
            if not p.specific.full_url:
                continue
            if not p.live:
                continue
            # Get cnetid and full name of page maintainer.
            if not hasattr(p.specific, 'page_maintainer'):
                continue
            page_maintainer_cnetid = ''
            if hasattr(p.specific.page_maintainer, 'cnetid'):
                page_maintainer_cnetid = p.specific.page_maintainer.cnetid
            page_maintainer_title = ''
            if hasattr(p.specific.page_maintainer, 'title'):
                page_maintainer_title  = p.specific.page_maintainer.title
        
            # Get cnetid and full name of page maintainer.
            if not hasattr(p.specific, 'editor'):
                continue
            editor_cnetid = ''
            if hasattr(p.specific.editor, 'cnetid'):
                editor_cnetid = p.specific.editor.cnetid
            editor_title = ''
            if hasattr(p.specific.editor, 'title'):
                editor_title  = p.specific.editor.title
        
            # Content specialist. (Note that these will always be blank on Loop.)
            content_specialist_cnetid = ''
            content_specialist_title = ''
            if hasattr(p.specific, 'content_specialist') and hasattr(p.specific.content_specialist, 'cnetid') and hasattr(p.specific.content_specialist, 'title'):
                content_specialist_cnetid = p.specific.content_specialist.cnetid
                content_specialist_title = p.specific.content_specialist.title
        
            # Skip this record if a cnetid has been specified. 
            if cnetid:
                if not page_maintainer_cnetid == cnetid and not editor_cnetid == cnetid and not content_specialist_cnetid == cnetid:
                    continue
            
            # Append to output.

            full_url = ''
            if p.specific.full_url:
                full_url = p.specific.full_url
                        
            latest_revision_created_at = ''
            if p.latest_revision_created_at:
                latest_revision_created_at = p.latest_revision_created_at.strftime('%Y-%m-%d %H:%M:%S')

            last_reviewed = ''
            if p.specific.last_reviewed:
                last_reviewed = p.specific.last_reviewed.strftime('%Y-%m-%d %H:%M:%S')

            records.append((full_url, p.title, latest_revision_created_at, last_reviewed, page_maintainer_cnetid, page_maintainer_title, editor_cnetid, editor_title, content_specialist_cnetid, content_specialist_title))
       
        writer = csv.writer(sys.stdout)
        for record in records:
            try:
                writer.writerow(record)
            except UnicodeEncodeError:
                pass
        
        return ''
            
        
        
