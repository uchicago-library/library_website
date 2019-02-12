# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from wagtail.core.models import Page, Site

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
        # Optional Argument.
        parser.add_argument('cnetid', nargs='?', type=str)

        # Optional named arguments
        parser.add_argument('-s', '--site',
            type=str,
            help='Restrict results to a specific site (Loop or Public).'
        )
        parser.add_argument('-r', '--role',
            type=str,
            help='Role of the person for whom pages are being looked up (page_maintainer, editor, content_specialist)'
        )

    def _get_pages(self, site_name):
        """
        Get pages by site name.

        Args:
            site_name: string, name of a site (Loop or Public) or None.

        Returns:
            page objects for a given site or all page objects
        """
        if site_name:
            site_obj = Site.objects.all().get(site_name=site_name)
            return Page.objects.in_site(site_obj).live()
        return Page.objects.live()


    def _in_scope(self, page, cnetid, role):
        """
        Determine if a page is in scope for the report.

        Args:
            page: page object

            cnetid: string

            role: string, the role for which you want the person
            to be on a given page

        Returns:
            boolean, whether or not the page should be
            included in the report. If there isn't a cnetid
            and role, the page should pass, however,
            if only a cnetid is passed a page with *any*
            role matching the cnet should pass.
        """
        # Convenience variables
        page_maintainer = self._get_attr(page.specific, 'page_maintainer')
        editor = self._get_attr(page.specific, 'editor')
        content_specialist = self._get_attr(page.specific, 'content_specialist')
        page_maintainer_cnetid = self._get_attr(page_maintainer, 'cnetid')
        editor_cnetid = self._get_attr(editor, 'cnetid')
        content_specialist_cnetid = self._get_attr(content_specialist, 'cnetid')

        # If there isn't a cnetid and there also isn't a role
        # all pages are being requested and any page should pass
        if not cnetid and not role:
            return True
        # If there's a cnetid but no role all pages with *any* role
        # matching the cnetid should pass
        elif cnetid and not role:
            if not page_maintainer_cnetid == cnetid and not editor_cnetid == cnetid and not content_specialist_cnetid == cnetid:
                return False
            return True
        # If we made it this far there is a cnetid and a role. Only
        # pages that have a role matching the cnetid should pass
        else:
            roles = {'page_maintainer': page_maintainer_cnetid,
                     'editor': editor_cnetid,
                     'content_specialist': content_specialist_cnetid}

            if str(roles[role]) == cnetid:
                return True
        # Return false if none of the other conditions are met
        return False


    def _get_attr(self, obj, attr):
        """
        Get an attribute for an object if it exists otherwise
        return an empty string.

        Args:
            object

            attr, sting attribute name


        Returns:
            attribute value or empty string
        """
        if hasattr(obj, attr):
            return getattr(obj, attr)
        return ''


    def _get_date_string(self, date):
        """
        Returns a formatted date string or an empty string
        if the input is wrong (e.g. None instead of a date object).

        Args:
            date: date object or bad input (usually None).

        Returns:
            string
        """
        if date:
            return date.strftime('%Y-%m-%d %H:%M:%S')


    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement this
        method. It may return a Unicode string which will be printed to
        stdout. More: https://docs.djangoproject.com/en/1.8/howto/custom
        -management-commands/#django.core.management.BaseCommand.handle
        """

        cnetid = options['cnetid']
        site_name = options['site']
        role = options['role']

        records = []
        records.append(('Page Title', 'Last Modified', 'Last Reviewed', 'Page Maintainer CNetID', 'Page Maintainer', 'Editor CNetID', 'Editor', 'Content Specialist CNetID', 'Content Specialist', 'URL'))
        for p in self._get_pages(site_name):
            page_maintainer = self._get_attr(p.specific, 'page_maintainer')
            page_maintainer_cnetid = self._get_attr(page_maintainer, 'cnetid')
            page_maintainer_title = self._get_attr(page_maintainer, 'title')
            editor = self._get_attr(p.specific, 'editor')
            editor_cnetid = self._get_attr(editor, 'cnetid')
            editor_title = self._get_attr(editor, 'title')
            content_specialist = self._get_attr(p.specific, 'content_specialist')
            content_specialist_cnetid = self._get_attr(content_specialist, 'cnetid')
            content_specialist_title = self._get_attr(content_specialist, 'title') if content_specialist else '' # Ternary operator because strings have a method called 'title'
            full_url = self._get_attr(p.specific, 'full_url')
            latest_revision_created_at = self._get_date_string(self._get_attr(p, 'latest_revision_created_at'))
            last_reviewed = self._get_date_string(self._get_attr(p.specific, 'last_reviewed'))

            # Skip this record if it's not in scope
            if not self._in_scope(p, cnetid, role):
                continue

            # Append to output.
            records.append((p.title, latest_revision_created_at, last_reviewed, page_maintainer_cnetid, page_maintainer_title, editor_cnetid, editor_title, content_specialist_cnetid, content_specialist_title, full_url))
       
        writer = csv.writer(sys.stdout)
        for record in records:
            try:
                writer.writerow(record)
            except UnicodeEncodeError:
                pass
        
        return ''
