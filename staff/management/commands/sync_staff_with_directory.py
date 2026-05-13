# -*- coding: utf-8 -*-
"""
Apply the diffs from `list_staff_wagtail --report-out-of-sync-staff` to Wagtail.

Intended to run from cron just before the existing out-of-sync report. Anything
this command can't or doesn't auto-handle will still surface in the next
report email and can be fixed manually.
"""

from __future__ import unicode_literals

import re

from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction
from wagtail.models import Page

from base.models import make_slug
from public.models import StaffPublicPage
from staff.models import StaffPage
from staff.utils import WagtailStaffReport
from units.models import UnitPage

# Page tree parents under which new pages are created. These ids are stable
# fixtures of the site and match the parents used when creating staff manually
# in the Wagtail admin.
STAFF_PAGE_PARENT_ID = 38
STAFF_PUBLIC_PAGE_PARENT_ID = 4273

# Format produced by `WagtailStaffReport._staff_out_of_sync()._format`:
#   "{cnetid} -{value}- ({field})"
LINE_RE = re.compile(r"^(?P<cnetid>\S+) -(?P<value>.*)- \((?P<field>[a-zA-Z]+)\)$")
PHONE_RE = re.compile(r"(\d{3}-\d{3}-\d{4})$")

SCALAR_FIELDS = ("officialName", "displayName", "positionTitle")
MULTI_FIELDS = ("email", "phoneFacultyExchange", "department")


def parse_phone_fx(value):
    """
    The report flattens (faculty_exchange, phone_number) into one space-joined
    string. Split it back: phone (if present) is anchored at end-of-string,
    everything else is the faculty exchange.
    """
    m = PHONE_RE.search(value)
    if m:
        return value[: m.start()].strip(), m.group(1)
    return value.strip(), ""


def split_name(display_name):
    """
    Split a display name into (first, middle, last) by whitespace.

    Args:
        display_name: a single-line name from the directory's displayName,
            e.g. "Pete Sample" or "Joan Q. Public".

    Returns:
        A 3-tuple of strings. Rules:
            - 0 tokens -> ("", "", "")
            - 1 token  -> (token, "", "")
            - 2 tokens -> (first, "", last)
            - 3+ tokens -> (first, " ".join(middles), last) — covers e.g.
              "Anne Marie Van Berg" -> ("Anne", "Marie Van", "Berg").

        StaffPage has first_name / middle_name / last_name; Django's User
        has only first_name / last_name, so callers updating User should
        use just the first and last slots (the middle is dropped on that
        side, matching the convention in `create_library_users`).
    """
    parts = display_name.strip().split()
    if not parts:
        return ("", "", "")
    if len(parts) == 1:
        return (parts[0], "", "")
    if len(parts) == 2:
        return (parts[0], "", parts[1])
    return (parts[0], " ".join(parts[1:-1]), parts[-1])


def empty_bundle():
    """
    Build the per-cnetid bundle that `_add_line` populates as it walks the
    two diff lists from the report.

    The "api" sub-dict holds values that appear in the directory but not in
    Wagtail (i.e. desired final state). The "wagtail" sub-dict holds values
    that appear in Wagtail but not the directory (i.e. things to remove).
    Scalar fields are stored as single values; multi-valued fields as sets.
    The "bare_*" booleans flag a bare-cnetid line on either side, which is
    how the report signals a new hire (bare in API only) or a departure
    (bare in Wagtail only).
    """
    return {
        "api": {f: set() for f in MULTI_FIELDS},
        "wagtail": {f: set() for f in MULTI_FIELDS},
        "bare_api": False,
        "bare_wagtail": False,
    }


class Command(BaseCommand):
    """
    Auto-apply staff directory diffs to Wagtail. Reads
    `WagtailStaffReport._staff_out_of_sync()` and updates StaffPage,
    StaffPublicPage, and User records to match the campus directory.

    Intended to run from cron just before the existing out-of-sync report,
    so anything this command misses or skips will still surface in the next
    report email and can be fixed manually.

    Example:
        python manage.py sync_staff_with_directory
        python manage.py sync_staff_with_directory --cnetid teststaff
    """

    help = (
        "Auto-apply staff directory diffs to Wagtail. Reads "
        "`WagtailStaffReport._staff_out_of_sync()` and updates StaffPage, "
        "StaffPublicPage, and User records to match the campus directory."
    )

    def add_arguments(self, parser):
        """
        Add optional named arguments. `--cnetid` restricts the run to a single
        person, primarily useful for smoke-testing changes against one record
        before letting cron loose on the full diff.
        """
        parser.add_argument(
            "--cnetid",
            type=str,
            default=None,
            help="Limit changes to a single CNetID (for testing).",
        )

    def handle(self, *args, **options):
        """
        Fetch the out-of-sync diff via `WagtailStaffReport._staff_out_of_sync()`,
        parse each line into a per-cnetid bundle, and apply the appropriate
        action (create / update / retire) for each cnetid. Each cnetid is
        wrapped in its own atomic transaction by `_apply`, so a failure on one
        person doesn't poison the rest of the run.

        Builds a `campus_directory_full_name -> UnitPage` lookup table once
        per run for use by `_apply_departments`.
        """
        report = WagtailStaffReport(
            sync_report=True,
            staff_report=False,
            all=False,
            cnetid=None,
            department=None,
            department_and_subdepartments=None,
            group=None,
            live=False,
            latest_revision_created_at=None,
            position_eliminated=False,
            supervises_students=False,
            supervisor_cnetid=None,
            supervisor_override=False,
            position_title=None,
        )
        missing_in_campus_directory, missing_in_wagtail = report._staff_out_of_sync()

        bundles = {}
        for line in missing_in_campus_directory:
            self._add_line(bundles, line, "wagtail")
        for line in missing_in_wagtail:
            self._add_line(bundles, line, "api")

        target = options.get("cnetid")
        if target:
            bundles = {k: v for k, v in bundles.items() if k == target}

        if not bundles:
            self.stdout.write("No diffs to apply.")
            return

        self._unit_by_campus_name = {
            u.get_campus_directory_full_name(): u for u in UnitPage.objects.live()
        }

        for cnetid in sorted(bundles.keys()):
            try:
                self._apply(cnetid, bundles[cnetid])
            except Exception as e:
                self.stdout.write(f"[{cnetid}] ERROR: {e}")

    def _add_line(self, bundles, line, side):
        """
        Parse one line from the out-of-sync report and route its value into
        the right slot in `bundles` (keyed by cnetid).

        Args:
            bundles: dict of cnetid -> bundle (mutated in place).
            line: a single report line. Either "{cnetid} -{value}- ({field})"
                or a bare "{cnetid}" indicating a new hire or departure.
            side: "api" if `line` came from the "missing in Wagtail" list, or
                "wagtail" if it came from the "missing in campus directory"
                list.
        """
        line = (line or "").strip()
        if not line:
            return
        m = LINE_RE.match(line)
        if m:
            cnetid = m.group("cnetid")
            field = m.group("field")
            value = m.group("value")
            bundle = bundles.setdefault(cnetid, empty_bundle())
            if field in SCALAR_FIELDS:
                bundle[side][field] = value
            elif field in MULTI_FIELDS:
                bundle[side][field].add(value)
        else:
            cnetid = line
            bundle = bundles.setdefault(cnetid, empty_bundle())
            if side == "api":
                bundle["bare_api"] = True
            else:
                bundle["bare_wagtail"] = True

    @transaction.atomic
    def _apply(self, cnetid, bundle):
        """
        Dispatch to the right branch for this cnetid. Wrapped in
        `transaction.atomic` so any failure inside a branch rolls back
        cleanly without affecting other cnetids in the same run.

        A bare-cnetid line on the API side means a new hire; on the Wagtail
        side means a departure. Anything else is a field-level update on an
        existing person.
        """
        if bundle["bare_api"]:
            self._create_new_staff(cnetid, bundle["api"])
        elif bundle["bare_wagtail"]:
            self._retire_staff(cnetid)
        else:
            self._update_existing_staff(cnetid, bundle)

    def _create_new_staff(self, cnetid, api):
        """
        Provision a brand-new staff member: a Django User (via the existing
        `create_library_user` command, which handles the Library + Editors
        group assignment), a StaffPage under STAFF_PAGE_PARENT_ID, and a
        StaffPublicPage under STAFF_PUBLIC_PAGE_PARENT_ID.

        Args:
            cnetid: the CNetID from the bare-cnetid line on the API side.
            api: the "api" sub-bundle, containing everything the directory
                knows about this person (officialName, displayName,
                positionTitle, emails, phone/faculty-exchanges, departments).

        The StaffPublicPage's `editor`, `page_maintainer`, and
        `content_specialist` are set to the newly-created StaffPage itself
        (self-managed); the `unit` is set to the top-level "Library"
        UnitPage. If no "Library" UnitPage exists, the StaffPublicPage is
        skipped and surfaces in the next report for manual handling.
        """
        display_name = api.get("displayName") or ""
        if not display_name:
            self.stdout.write(f"[{cnetid}] SKIP new hire: no displayName in report")
            return

        official_name = api.get("officialName") or display_name
        position_title = api.get("positionTitle") or ""
        first, middle, last = split_name(display_name)
        primary_email = next(iter(sorted(api["email"])), "")

        # Reuse the existing user-creation command (handles Library + Editors
        # group assignment and protected-name overrides).
        call_command(
            "create_library_user",
            cnetid,
            first,
            last,
            primary_email,
            "False",
            is_active="True",
        )
        self.stdout.write(f"[{cnetid}] CREATE User: {first} {last}")

        staff_parent = Page.objects.get(id=STAFF_PAGE_PARENT_ID)
        staff = StaffPage(
            title=display_name,
            slug=make_slug(display_name),
            cnetid=cnetid,
            display_name=display_name,
            official_name=official_name,
            first_name=first,
            middle_name=middle,
            last_name=last,
            position_title=position_title,
        )
        staff_parent.add_child(instance=staff)

        for em in sorted(api["email"]):
            staff.staff_page_email.create(email=em)
        for value in sorted(api["phoneFacultyExchange"]):
            fx, phone = parse_phone_fx(value)
            staff.staff_page_phone_faculty_exchange.create(
                faculty_exchange=fx, phone_number=phone
            )
        self._apply_departments(staff, cnetid, api["department"], set())

        staff.save_revision().publish()
        self.stdout.write(f"[{cnetid}] CREATE StaffPage: '{display_name}'")

        try:
            library_unit = UnitPage.objects.get(title="Library")
        except UnitPage.DoesNotExist:
            self.stdout.write(
                f"[{cnetid}] SKIP StaffPublicPage: no UnitPage titled 'Library' found"
            )
            return

        public_parent = Page.objects.get(id=STAFF_PUBLIC_PAGE_PARENT_ID)
        public = StaffPublicPage(
            title=display_name,
            slug=make_slug(display_name),
            cnetid=cnetid,
            editor=staff,
            page_maintainer=staff,
            content_specialist=staff,
            unit=library_unit,
        )
        public_parent.add_child(instance=public)
        public.save_revision().publish()
        self.stdout.write(f"[{cnetid}] CREATE StaffPublicPage: '{display_name}'")

    def _retire_staff(self, cnetid):
        """
        Mark a departed staff member's User as inactive. The unpublishing of
        the StaffPage and StaffPublicPage is handled by the existing
        `post_save` signal on User at `staff/wagtail_hooks.py:112`, so this
        method just flips the flag and saves; the hook does the rest.

        Idempotent: a user that's already inactive is skipped with a log
        line. A missing User account is also skipped (likely an orphan
        StaffPage that needs manual cleanup).
        """
        try:
            user = User.objects.get(username=cnetid)
        except User.DoesNotExist:
            self.stdout.write(f"[{cnetid}] SKIP departure: no User account")
            return
        if not user.is_active:
            self.stdout.write(f"[{cnetid}] SKIP departure: user already inactive")
            return
        user.is_active = False
        user.save()
        self.stdout.write(
            f"[{cnetid}] RETIRE: deactivated User; post_save hook unpublishes pages"
        )

    def _update_existing_staff(self, cnetid, bundle):
        """
        Apply field-level updates from the directory to an existing
        StaffPage, plus the cascading updates that go with them.

        Scalar fields (officialName, displayName, positionTitle) are
        overwritten from the API side. A change to displayName cascades to
        `StaffPage.title`, the derived `first_name`/`last_name` on both
        StaffPage and the matching Django User, and `StaffPublicPage.title`.

        Multi-valued fields (email, phoneFacultyExchange, department) are
        synced as a "remove wagtail-only values, add api-only values"
        pair — the directory is authoritative. Department updates short-
        circuit if any API-side department fails to resolve to a UnitPage;
        see `_apply_departments`.

        Note: uses plain `staff.save()` rather than `save_revision().publish()`
        to avoid a modelcluster footgun where serializing the page's
        in-memory cluster captures stale child-row state and `.publish()`
        then reverts the direct .create()/.delete() we just performed on
        emails and phone-FX rows.
        """
        try:
            staff = StaffPage.objects.get(cnetid=cnetid)
        except StaffPage.DoesNotExist:
            self.stdout.write(f"[{cnetid}] SKIP update: no StaffPage")
            return

        api = bundle["api"]
        wag = bundle["wagtail"]

        new_display = api.get("displayName")
        new_official = api.get("officialName")
        new_position = api.get("positionTitle")
        first, middle, last = split_name(new_display) if new_display else ("", "", "")

        if new_display:
            staff.display_name = new_display
            staff.title = new_display
            staff.first_name = first
            staff.middle_name = middle
            staff.last_name = last
            self.stdout.write(f"[{cnetid}] UPDATE displayName -> {new_display}")
        if new_official is not None:
            staff.official_name = new_official
            self.stdout.write(f"[{cnetid}] UPDATE officialName -> {new_official}")
        if new_position is not None:
            staff.position_title = new_position
            self.stdout.write(f"[{cnetid}] UPDATE positionTitle -> {new_position}")

        for em in sorted(wag["email"]):
            deleted, _ = staff.staff_page_email.filter(email=em).delete()
            if deleted:
                self.stdout.write(f"[{cnetid}] REMOVE email: {em}")
        for em in sorted(api["email"]):
            staff.staff_page_email.create(email=em)
            self.stdout.write(f"[{cnetid}] ADD email: {em}")

        for value in sorted(wag["phoneFacultyExchange"]):
            fx, phone = parse_phone_fx(value)
            deleted, _ = staff.staff_page_phone_faculty_exchange.filter(
                faculty_exchange=fx, phone_number=phone
            ).delete()
            if deleted:
                self.stdout.write(f"[{cnetid}] REMOVE phone/FX: '{fx}' '{phone}'")
        for value in sorted(api["phoneFacultyExchange"]):
            fx, phone = parse_phone_fx(value)
            staff.staff_page_phone_faculty_exchange.create(
                faculty_exchange=fx, phone_number=phone
            )
            self.stdout.write(f"[{cnetid}] ADD phone/FX: '{fx}' '{phone}'")

        self._apply_departments(staff, cnetid, api["department"], wag["department"])

        staff.save()

        if new_display:
            try:
                user = User.objects.get(username=cnetid)
                user.first_name = first
                user.last_name = last
                user.save()
                self.stdout.write(f"[{cnetid}] UPDATE User name -> {first} {last}")
            except User.DoesNotExist:
                self.stdout.write(f"[{cnetid}] WARN: no User to update name on")

            try:
                public = StaffPublicPage.objects.get(cnetid=cnetid)
                public.title = new_display
                public.save()
                self.stdout.write(
                    f"[{cnetid}] UPDATE StaffPublicPage title -> {new_display}"
                )
            except StaffPublicPage.DoesNotExist:
                self.stdout.write(
                    f"[{cnetid}] WARN: no StaffPublicPage to update title on"
                )

    def _apply_departments(self, staff, cnetid, api_to_add, wag_to_remove):
        """
        Resolve every API-side department string to a UnitPage before touching
        anything. If any one fails to resolve, skip all department updates for
        this person; the next report will surface it for manual handling.
        """
        resolved = {}
        for name in api_to_add:
            unit = self._unit_by_campus_name.get(name)
            if not unit:
                self.stdout.write(
                    f"[{cnetid}] SKIP department updates: cannot resolve "
                    f"'{name}' to a UnitPage"
                )
                return
            resolved[name] = unit

        children = list(staff.staff_page_units.all())
        for name in wag_to_remove:
            for child in children:
                if (
                    child.library_unit
                    and child.library_unit.get_campus_directory_full_name() == name
                ):
                    child.delete()
                    self.stdout.write(f"[{cnetid}] REMOVE department: {name}")
                    break

        for name, unit in resolved.items():
            staff.staff_page_units.create(library_unit=unit)
            self.stdout.write(f"[{cnetid}] ADD department: {name}")
