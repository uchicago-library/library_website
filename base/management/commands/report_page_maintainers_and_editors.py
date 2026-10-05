# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import csv
import sys

from django.core.management.base import BaseCommand
from wagtail.models import Page, Site


class Command(BaseCommand):
    """
    Produce a report of pages for which a given person is the maintainer,
    editor or content specialist.

    Example:
        python manage.py report_page_maintainers_and_editors cnetid
    """

    HEADER = (
        "URL",
        "Page Title",
        "Last Modified",
        "Last Reviewed",
        "Page Maintainer CNetID",
        "Page Maintainer",
        "Editor CNetID",
        "Editor",
        "Content Specialist CNetID",
        "Content Specialist",
        "Unit",
        "Page Type",
        "Section Start",
        "Total Number of Edits",
        "Creation Date",
        "Title Tag",
        "Meta Description",
    )

    def add_arguments(self, parser):
        """
        Add required positional options and optional
        named arguments.
        """
        # Optional Argument.
        parser.add_argument("cnetid", nargs="?", type=str)

        # Optional named arguments
        parser.add_argument(
            "-s",
            "--site",
            type=str,
            help="Restrict results to a specific site (Loop or Public).",
        )
        parser.add_argument(
            "-r",
            "--role",
            type=str,
            help="Role of the person for whom pages are being looked \
            up (page_maintainer, editor, content_specialist)",
        )

    def _get_pages(self, cnetid, site_name, role):
        """
        Get pages that are in scope for a given query.

        Args:
            site_name: string, name of a site (Loop or Public) or None.

        Returns:
            page objects for a given site or all page objects
        """
        # Start with pages for a specific site or get all pages
        # if a specific site wasn't given
        if site_name:
            # Site specific pages
            site_obj = Site.objects.all().get(site_name=site_name)
            pages = Page.objects.in_site(site_obj).live().specific().iterator()
        else:
            # All pages
            pages = Page.objects.live().specific().iterator()

        # If a cnetid and role is given, return all pages where
        # the role is set to a user with the given cnet id. If
        # only a cnetid is given, return all pages where any
        # role matches the given cnetid
        if cnetid:
            if role:
                return self._get_pages_with_role_for_cnet(
                    pages, cnetid, site_name, role
                )
            return self._get_pages_with_any_role_for_cnet(
                pages, cnetid, site_name, role
            )

        # If we made it this far, return all pages
        return self._parse_pages(pages, cnetid, site_name, role)

    def _parse_pages(self, pages, cnetid, site_name, role):
        """
        Filter a generator of pages and return a new generator
        of pages with information parsed out for each page.

        Args:
            pages: generator of page objects

            cnetid: string

            site_name: string

            role: string, 'page_maintainer', 'editor' or 'content_specialist'

        Returns:
            generator of page objects
        """
        yield self.HEADER
        for page in pages:
            yield self.get_row(page, cnetid, site_name, role)

    def _get_pages_with_role_for_cnet(self, pages, cnetid, site_name, role):
        """
        Filter a generator of pages and return a new generator
        of pages where a given role is set to a user with a
        given cnetid.

        Args:
            pages: generator of page objects

            cnetid: string

            site_name: string

            role: string, 'page_maintainer', 'editor' or 'content_specialist'

        Returns:
            generator of page objects
        """
        yield self.HEADER
        for page in pages:
            user = self._get_attr(page, role)
            user_cnetid = self._get_attr(user, "cnetid")
            if user_cnetid == cnetid:
                yield self.get_row(page, cnetid, site_name, role)

    def _get_pages_with_any_role_for_cnet(self, pages, cnetid, site_name, role):
        """
        Filter a generator to return any page that has any role
        assigned to a user with a given cnetid.

        Args:
            pages: generator of page objects

            cnetid: string

            site_name: string

            role: string

        Returns:
            generator of page objects
        """
        yield self.HEADER
        for page in pages:
            page_maintainer = self._get_attr(page, "page_maintainer")
            editor = self._get_attr(page, "editor")
            content_specialist = self._get_attr(page, "content_specialist")
            page_maintainer_cnetid = self._get_attr(page_maintainer, "cnetid")
            editor_cnetid = self._get_attr(editor, "cnetid")
            content_specialist_cnetid = self._get_attr(content_specialist, "cnetid")
            if (
                page_maintainer_cnetid == cnetid
                or editor_cnetid == cnetid
                or content_specialist_cnetid == cnetid
            ):
                yield self.get_row(page, cnetid, site_name, role)

    def get_row(self, p, cnetid, site_name, role):
        """
        Args:
            p: page object

            cnetid: string

            site_name: string

            role: string

        Returns:
            list of tuples containing data about pages to be converted
            into a csv. The first tuple in the list represents the column
            names (header) that will be used on the spreadsheet.
        """
        row = []
        page_maintainer = self._get_attr(p, "page_maintainer")
        page_maintainer_cnetid = self._get_attr(page_maintainer, "cnetid")
        page_maintainer_title = self._get_attr(page_maintainer, "title")
        editor = self._get_attr(p, "editor")
        editor_cnetid = self._get_attr(editor, "cnetid")
        editor_title = self._get_attr(editor, "title")
        content_specialist = self._get_attr(p, "content_specialist")
        content_specialist_cnetid = self._get_attr(content_specialist, "cnetid")
        content_specialist_title = self._get_attr(content_specialist, "title")
        full_url = self._get_attr(p, "full_url")
        latest_revision_created_at = self._get_date_string(
            self._get_attr(p, "latest_revision_created_at")
        )
        last_reviewed = self._get_date_string(self._get_attr(p, "last_reviewed"))
        unit = self._get_attr(p, "unit")
        page_type = p.cached_content_type.name
        section_start = self._get_attr(p, "start_sidebar_from_here")
        title_tag = self._get_attr(p, "seo_title")
        meta_desc = self._get_attr(p, "search_description")
        total_edits = self._get_attr(p, "revisions").count()
        created_date = self._get_date_string(self._get_attr(p, "first_published_at"))

        # Append to output.
        row.append(
            (
                full_url,
                p.title,
                latest_revision_created_at,
                last_reviewed,
                page_maintainer_cnetid,
                page_maintainer_title,
                editor_cnetid,
                editor_title,
                content_specialist_cnetid,
                content_specialist_title,
                unit,
                page_type,
                section_start,
                total_edits,
                created_date,
                title_tag,
                meta_desc,
            )
        )
        return row[0]

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
            # Since string attributes have a method called title
            if obj == "" and attr == "title":
                return ""
            return getattr(obj, attr)
        return ""

    def _get_date_string(self, date):
        """
        Returns a formatted date string or an empty string if the input
        is wrong (e.g. None instead of a date object). Mostly just a
        wrapper function to hold configuration.

        Args:
            date: date object or bad input (usually None).

        Returns:
            string
        """
        if date:
            return date.strftime("%Y-%m-%d %H:%M:%S")
        return ""

    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement this
        method. It may return a Unicode string which will be printed to
        stdout. More: https://docs.djangoproject.com/en/1.8/howto/custom
        -management-commands/#django.core.management.BaseCommand.handle
        """

        cnetid = options["cnetid"]
        site_name = options["site"]
        role = options["role"]

        writer = csv.writer(sys.stdout)
        for record in self._get_pages(cnetid, site_name, role):
            try:
                writer.writerow(record)
            except UnicodeEncodeError:
                pass

        return ""
