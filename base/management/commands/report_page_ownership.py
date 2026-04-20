# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import csv
import sys

from django.core.management.base import BaseCommand
from wagtail.models import Page, Site


class Command(BaseCommand):
    """
    Produce a page ownership report as CSV.

    Example:
        python manage.py report_page_ownership
        python manage.py report_page_ownership cnetid
        python manage.py report_page_ownership cnetid --role editor --site Public
    """

    HEADER = (
        "URL",
        "Page Owner",
        "Page Maintainer",
        "Editor",
        "Content Specialist",
        "Unit",
        "Page Type",
        "Creation Date",
        "Total Number of Edits",
        "Last Activity Date",
        "Last Activity By",
    )

    def add_arguments(self, parser):
        """
        Add required positional options and optional
        named arguments.
        """
        # Optional argument.
        parser.add_argument("cnetid", nargs="?", type=str)

        # Optional named arguments.
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
            help="Role of the person for whom pages are being looked up "
            "(page_maintainer, editor, content_specialist)",
        )

    def _get_pages(self, cnetid, site_name):
        """
        Get pages that are in scope for a given query.

        Args:
            site_name: string, name of a site (Loop or Public) or None.

        Returns:
            generator of page objects
        """
        if site_name:
            site_obj = Site.objects.all().get(site_name=site_name)
            return Page.objects.in_site(site_obj).live().specific().iterator()
        return Page.objects.live().specific().iterator()

    def _get_attr(self, obj, attr):
        """
        Get an attribute for an object if it exists otherwise
        return an empty string.

        Args:
            object

            attr, string attribute name

        Returns:
            attribute value or empty string
        """
        if hasattr(obj, attr):
            # Since string attributes have a method called title
            if obj == "" and attr == "title":
                return ""
            return getattr(obj, attr)
        return ""

    def _get_person_display_name(self, person):
        """
        Return a staff person's display name.
        """
        return self._get_attr(person, "title")

    def _get_user_display_name(self, user):
        """
        Return a user display name.
        """
        full_name = self._get_attr(user, "get_full_name")
        if full_name and callable(full_name):
            value = full_name().strip()
            if value:
                return value

        username = self._get_attr(user, "username")
        if username:
            return username

        email = self._get_attr(user, "email")
        if email:
            return email

        return ""

    def _get_last_revision(self, page):
        """
        Get the latest revision object for a page.
        """
        revisions = self._get_attr(page, "revisions")
        if revisions:
            return revisions.order_by("-created_at").first()
        return None

    def _get_last_activity_date(self, page):
        """
        Best-effort last activity timestamp.

        Uses latest_revision_created_at because it captures the most recent
        revision activity, including publish-related revisions.
        """
        dt = self._get_attr(page, "latest_revision_created_at")
        if dt:
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        return ""

    def _get_last_activity_by(self, page):
        """
        Best-effort person for the latest activity.

        Prefers latest revision user and falls back to page owner.
        """
        revision = self._get_last_revision(page)
        user = self._get_attr(revision, "user")
        if not user:
            user = self._get_attr(page, "owner")

        return self._get_user_display_name(user)

    def _get_creation_date(self, page):
        """
        Best-effort creation date.

        Prefers first_published_at and falls back to the earliest revision.
        """
        first_published_at = self._get_attr(page, "first_published_at")
        if first_published_at:
            return first_published_at.strftime("%Y-%m-%d %H:%M:%S")

        revisions = self._get_attr(page, "revisions")
        if revisions:
            first_revision = revisions.order_by("created_at").first()
            created_at = self._get_attr(first_revision, "created_at")
            if created_at:
                return created_at.strftime("%Y-%m-%d %H:%M:%S")

        return ""

    def _get_total_number_of_edits(self, page):
        """
        Return number of revisions if available.
        """
        revisions = self._get_attr(page, "revisions")
        if revisions:
            return revisions.count()
        return ""

    def _page_matches_cnetid_filter(self, page, cnetid, role):
        """
        Return True if a page matches cnetid/role filters.
        """
        if not cnetid:
            return True

        if role:
            person = self._get_attr(page, role)
            return self._get_attr(person, "cnetid") == cnetid

        page_maintainer = self._get_attr(page, "page_maintainer")
        editor = self._get_attr(page, "editor")
        content_specialist = self._get_attr(page, "content_specialist")

        return (
            self._get_attr(page_maintainer, "cnetid") == cnetid
            or self._get_attr(editor, "cnetid") == cnetid
            or self._get_attr(content_specialist, "cnetid") == cnetid
        )

    def _get_row(self, page):
        """
        Convert a page object to one output row.
        """
        page_maintainer = self._get_attr(page, "page_maintainer")
        editor = self._get_attr(page, "editor")
        content_specialist = self._get_attr(page, "content_specialist")
        page_owner = self._get_attr(page, "owner")

        url = self._get_attr(page, "full_url")
        unit = self._get_attr(page, "unit")
        page_type = self._get_attr(self._get_attr(page, "cached_content_type"), "name")

        return (
            url,
            self._get_user_display_name(page_owner),
            self._get_person_display_name(page_maintainer),
            self._get_person_display_name(editor),
            self._get_person_display_name(content_specialist),
            str(unit) if unit else "",
            page_type,
            self._get_creation_date(page),
            self._get_total_number_of_edits(page),
            self._get_last_activity_date(page),
            self._get_last_activity_by(page),
        )

    def _iter_records(self, cnetid, site_name, role):
        """
        Yield header and matching rows.
        """
        yield self.HEADER
        for page in self._get_pages(cnetid, site_name):
            if self._page_matches_cnetid_filter(page, cnetid, role):
                yield self._get_row(page)

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
        for record in self._iter_records(cnetid, site_name, role):
            try:
                writer.writerow(record)
            except UnicodeEncodeError:
                pass

        return ""