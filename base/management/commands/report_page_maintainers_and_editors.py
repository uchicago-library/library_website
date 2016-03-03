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
        # Required positional options
        parser.add_argument('cnetid', type=str)

    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement this 
        method. It may return a Unicode string which will be printed to 
        stdout. More: https://docs.djangoproject.com/en/1.8/howto/custom
        -management-commands/#django.core.management.BaseCommand.handle
        """

        try:
            cnetid = options['cnetid']
        except:
            sys.exit(1)

        display_all = False
        
        records = []
        records.append(('URL', 'Page Title', 'Last Modified', 'Page Maintainer CNetID', 'Page Maintainer', 'Editor CNetID', 'Editor', 'Content Specialist CNetID', 'Content Specialist'))
        for p in Page.objects.all():
            # Skip pages that aren't live. 
            if not p.specific.full_url:
                continue
            # Get cnetid and full name of page maintainer.
            if not hasattr(p.specific, 'page_maintainer'):
                continue
            if hasattr(p.specific.page_maintainer, 'cnetid'):
                page_maintainer_cnetid = p.specific.page_maintainer.cnetid
            else:
                page_maintainer_cnetid = ''
            if hasattr(p.specific.page_maintainer, 'title'):
                page_maintainer_title  = p.specific.page_maintainer.title
            else:
                page_maintainer_title = ''
        
            # Get cnetid and full name of page maintainer.
            if not hasattr(p.specific, 'editor'):
                continue
            if hasattr(p.specific.editor, 'cnetid'):
                editor_cnetid = p.specific.editor.cnetid
            else:
                editor_cnetid = ''
            if hasattr(p.specific.editor, 'title'):
                editor_title  = p.specific.editor.title
            else:
                editor_title = ''
        
            # Content specialist. (Note that these will always be blank on Loop.)
            if hasattr(p.specific, 'content_specialist') and hasattr(p.specific.content_specialist, 'cnetid') and hasattr(p.specific.content_specialist, 'title'):
                content_specialist_cnetid = p.specific.content_specialist.cnetid
                content_specialist_title = p.specific.content_specialist.title
            else:
                content_specialist_cnetid = ''
                content_specialist_title = ''
        
            # Skip this record if a cnetid has been specified. 
            if not display_all:
                if not page_maintainer_cnetid == cnetid and not editor_cnetid == cnetid and not content_specialist_cnetid == cnetid:
                    continue
            
            # Append to output.
            records.append((p.specific.full_url, p.title, p.latest_revision_created_at, page_maintainer_cnetid, page_maintainer_title, editor_cnetid, editor_title, content_specialist_cnetid, content_specialist_title))
       
        output = io.StringIO() 
        writer = csv.writer(output)
        for record in records:
            writer.writerow(record)
        
        return output.getvalue()
            
        
        
