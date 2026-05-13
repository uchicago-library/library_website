"""
Tests for the `sync_staff_with_directory` management command.
"""

from io import StringIO
from unittest.mock import patch

from django.contrib.auth.models import Group, User
from django.core.management import call_command
from django.test import SimpleTestCase, TestCase
from wagtail.models import Page

from public.models import StaffPublicPage
from staff.management.commands import sync_staff_with_directory as syncmod
from staff.management.commands.sync_staff_with_directory import (
    LINE_RE,
    parse_phone_fx,
    split_name,
)
from staff.models import StaffPage
from units.models import UnitPage


class ParsingHelpersTest(SimpleTestCase):
    """Pure-function tests with no DB."""

    def test_parse_phone_fx_with_fx_and_phone(self):
        self.assertEqual(
            parse_phone_fx("JRL 180A 773-795-1085"), ("JRL 180A", "773-795-1085")
        )

    def test_parse_phone_fx_with_fx_only(self):
        self.assertEqual(parse_phone_fx("JRL 180A"), ("JRL 180A", ""))

    def test_parse_phone_fx_with_phone_only(self):
        self.assertEqual(parse_phone_fx("773-795-1085"), ("", "773-795-1085"))

    def test_parse_phone_fx_empty(self):
        self.assertEqual(parse_phone_fx(""), ("", ""))

    def test_split_name_two_parts(self):
        self.assertEqual(split_name("Pete Sample"), ("Pete", "", "Sample"))

    def test_split_name_one_part(self):
        self.assertEqual(split_name("Mononym"), ("Mononym", "", ""))

    def test_split_name_three_parts(self):
        self.assertEqual(split_name("Joan Q Public"), ("Joan", "Q", "Public"))

    def test_split_name_four_parts_joins_middles(self):
        self.assertEqual(
            split_name("Anne Marie Van Berg"), ("Anne", "Marie Van", "Berg")
        )

    def test_split_name_empty(self):
        self.assertEqual(split_name(""), ("", "", ""))

    def test_line_re_scalar_field(self):
        m = LINE_RE.match("teststaff -New Name- (displayName)")
        self.assertIsNotNone(m)
        self.assertEqual(m.group("cnetid"), "teststaff")
        self.assertEqual(m.group("value"), "New Name")
        self.assertEqual(m.group("field"), "displayName")

    def test_line_re_value_contains_hyphens(self):
        # Department strings include " - " separators between hierarchy levels.
        m = LINE_RE.match("teststaff -Library - Reference- (department)")
        self.assertIsNotNone(m)
        self.assertEqual(m.group("value"), "Library - Reference")
        self.assertEqual(m.group("field"), "department")

    def test_line_re_bare_cnetid_does_not_match(self):
        self.assertIsNone(LINE_RE.match("teststaff"))


class SyncStaffWithDirectoryTest(TestCase):
    """Integration tests that exercise the full command against a real DB."""

    @classmethod
    def setUpTestData(cls):
        try:
            welcome = Page.objects.get(path="00010001")
        except Page.DoesNotExist:
            root = Page.objects.create(depth=1, path="0001", slug="root", title="Root")
            welcome = Page(path="00010001", slug="welcome", title="Welcome")
            root.add_child(instance=welcome)
        cls.welcome = welcome

        admin_staff = StaffPage(cnetid="admin", slug="admin-staff", title="Admin Staff")
        welcome.add_child(instance=admin_staff)
        cls.admin_staff = admin_staff

        cls.library_unit = UnitPage(
            slug="library",
            title="Library",
            display_in_dropdown=True,
            display_in_campus_directory=False,
            editor=admin_staff,
            page_maintainer=admin_staff,
        )
        welcome.add_child(instance=cls.library_unit)

        cls.unit = UnitPage(
            slug="reference",
            title="Reference",
            display_in_dropdown=True,
            display_in_campus_directory=True,
            editor=admin_staff,
            page_maintainer=admin_staff,
        )
        cls.library_unit.add_child(instance=cls.unit)

        # Distinct parents for new StaffPage / StaffPublicPage so the slug
        # derived from displayName doesn't collide between them.
        cls.staff_parent = Page(slug="staff-index", title="Staff Index")
        welcome.add_child(instance=cls.staff_parent)
        cls.public_parent = Page(slug="public-index", title="Public Index")
        welcome.add_child(instance=cls.public_parent)

        # Groups that `create_library_user` requires for new hires.
        Group.objects.get_or_create(name="Library")
        Group.objects.get_or_create(name="Editors")

    def setUp(self):
        self.user = User.objects.create_user(
            username="teststaff",
            password="password",
            first_name="Pete",
            last_name="Sample",
            is_active=True,
        )
        self.staff_page = StaffPage(
            cnetid="teststaff",
            slug="test-staff",
            title="Pete Sample",
            display_name="Pete Sample",
            official_name="Peter Sample",
            first_name="Pete",
            last_name="Sample",
            position_title="Old Title",
        )
        self.welcome.add_child(instance=self.staff_page)
        self.staff_page.save_revision().publish()

        self.public_page = StaffPublicPage(
            cnetid="teststaff",
            slug="test-staff-public",
            title="Pete Sample",
            editor=self.admin_staff,
            page_maintainer=self.admin_staff,
            content_specialist=self.admin_staff,
            unit=self.unit,
        )
        self.welcome.add_child(instance=self.public_page)
        self.public_page.save_revision().publish()

    def _run(self, in_wagtail, in_api, **kwargs):
        """Run the command with a mocked report. Returns captured stdout."""
        out = StringIO()
        fake_diff = (in_wagtail, in_api)
        with patch(
            "staff.management.commands.sync_staff_with_directory."
            "WagtailStaffReport._staff_out_of_sync",
            return_value=fake_diff,
        ):
            call_command("sync_staff_with_directory", stdout=out, **kwargs)
        return out.getvalue()

    # --- existing-staff scalar updates ---

    def test_position_title_update(self):
        self._run(
            in_wagtail=["teststaff -Old Title- (positionTitle)"],
            in_api=["teststaff -New Title- (positionTitle)"],
        )
        self.staff_page.refresh_from_db()
        self.assertEqual(self.staff_page.position_title, "New Title")

    def test_display_name_update_cascades(self):
        self._run(
            in_wagtail=["teststaff -Pete Sample- (displayName)"],
            in_api=["teststaff -Pete S. Sample- (displayName)"],
        )
        self.staff_page.refresh_from_db()
        self.public_page.refresh_from_db()
        self.user.refresh_from_db()

        self.assertEqual(self.staff_page.display_name, "Pete S. Sample")
        self.assertEqual(self.staff_page.title, "Pete S. Sample")
        self.assertEqual(self.staff_page.first_name, "Pete")
        self.assertEqual(self.staff_page.middle_name, "S.")
        self.assertEqual(self.staff_page.last_name, "Sample")
        self.assertEqual(self.public_page.title, "Pete S. Sample")
        # Django User has no middle_name field; middle is dropped on that side.
        self.assertEqual(self.user.first_name, "Pete")
        self.assertEqual(self.user.last_name, "Sample")

    # --- child rows: save_revision().publish() must capture them ---

    def test_email_replacement(self):
        self.staff_page.staff_page_email.create(email="old@uchicago.edu")

        self._run(
            in_wagtail=["teststaff -old@uchicago.edu- (email)"],
            in_api=["teststaff -new@uchicago.edu- (email)"],
        )
        # Re-fetch from DB; refresh_from_db() doesn't reset modelcluster's
        # per-instance child cache.
        staff = StaffPage.objects.get(cnetid="teststaff")
        emails = sorted(e.email for e in staff.staff_page_email.all())
        self.assertEqual(emails, ["new@uchicago.edu"])

    def test_phone_fx_upgrade_dakotaw_case(self):
        """
        Wagtail row has FX only; API row has the same FX plus a phone number.
        After sync, exactly one row should remain with both fields populated.
        """
        self.staff_page.staff_page_phone_faculty_exchange.create(
            faculty_exchange="JRL 180A", phone_number=""
        )

        self._run(
            in_wagtail=["teststaff -JRL 180A- (phoneFacultyExchange)"],
            in_api=["teststaff -JRL 180A 773-795-1085- (phoneFacultyExchange)"],
        )

        staff = StaffPage.objects.get(cnetid="teststaff")
        rows = list(staff.staff_page_phone_faculty_exchange.all())
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].faculty_exchange, "JRL 180A")
        self.assertEqual(rows[0].phone_number, "773-795-1085")

    # --- departments ---

    def test_department_add(self):
        self._run(
            in_wagtail=[],
            in_api=["teststaff -Reference- (department)"],
        )
        staff = StaffPage.objects.get(cnetid="teststaff")
        units = [
            c.library_unit.pk for c in staff.staff_page_units.all() if c.library_unit
        ]
        self.assertEqual(units, [self.unit.pk])

    def test_department_resolution_failure_skips_dept_but_applies_others(self):
        self._run(
            in_wagtail=["teststaff -Old Title- (positionTitle)"],
            in_api=[
                "teststaff -New Title- (positionTitle)",
                "teststaff -Does Not Exist- (department)",
            ],
        )
        staff = StaffPage.objects.get(cnetid="teststaff")
        self.assertEqual(staff.position_title, "New Title")
        self.assertEqual(staff.staff_page_units.count(), 0)

    # --- departures ---

    def test_retire_deactivates_user_and_hook_unpublishes_pages(self):
        self._run(
            in_wagtail=["teststaff"],
            in_api=[],
        )
        self.user.refresh_from_db()
        self.staff_page.refresh_from_db()
        self.public_page.refresh_from_db()
        self.assertFalse(self.user.is_active)
        # The post_save signal on User unpublishes both pages.
        self.assertFalse(self.staff_page.live)
        self.assertFalse(self.public_page.live)

    def test_retire_skips_already_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        out = self._run(
            in_wagtail=["teststaff"],
            in_api=[],
        )
        self.assertIn("already inactive", out)

    # --- new hires ---

    def test_new_hire_creates_user_and_pages(self):
        with (
            patch.object(syncmod, "STAFF_PAGE_PARENT_ID", self.staff_parent.pk),
            patch.object(syncmod, "STAFF_PUBLIC_PAGE_PARENT_ID", self.public_parent.pk),
        ):
            out = self._run(
                in_wagtail=[],
                in_api=[
                    "newhire",
                    "newhire -Jane New- (displayName)",
                    "newhire -Jane A. New- (officialName)",
                    "newhire -Librarian- (positionTitle)",
                    "newhire -jane@uchicago.edu- (email)",
                    "newhire -JRL 200 773-702-1000- (phoneFacultyExchange)",
                    "newhire -Reference- (department)",
                ],
            )
        self.assertNotIn("ERROR", out, msg=f"Command logged an error:\n{out}")

        user = User.objects.get(username="newhire")
        self.assertTrue(user.is_active)
        self.assertEqual(user.first_name, "Jane")
        self.assertEqual(user.last_name, "New")
        self.assertSetEqual(
            set(user.groups.values_list("name", flat=True)),
            {"Library", "Editors"},
        )

        staff = StaffPage.objects.get(cnetid="newhire")
        self.assertEqual(staff.display_name, "Jane New")
        self.assertEqual(staff.official_name, "Jane A. New")
        self.assertEqual(staff.position_title, "Librarian")
        self.assertTrue(staff.live)

        emails = [e.email for e in staff.staff_page_email.all()]
        self.assertEqual(emails, ["jane@uchicago.edu"])

        rows = list(staff.staff_page_phone_faculty_exchange.all())
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].faculty_exchange, "JRL 200")
        self.assertEqual(rows[0].phone_number, "773-702-1000")

        unit_ids = [
            c.library_unit.pk for c in staff.staff_page_units.all() if c.library_unit
        ]
        self.assertEqual(unit_ids, [self.unit.pk])

        public = StaffPublicPage.objects.get(cnetid="newhire")
        self.assertEqual(public.title, "Jane New")
        self.assertTrue(public.live)

    def test_new_hire_without_display_name_is_skipped(self):
        with (
            patch.object(syncmod, "STAFF_PAGE_PARENT_ID", self.staff_parent.pk),
            patch.object(syncmod, "STAFF_PUBLIC_PAGE_PARENT_ID", self.public_parent.pk),
        ):
            out = self._run(
                in_wagtail=[],
                in_api=["newhire"],
            )
        self.assertIn("SKIP new hire", out)
        self.assertFalse(User.objects.filter(username="newhire").exists())
        self.assertFalse(StaffPage.objects.filter(cnetid="newhire").exists())

    # --- filtering ---

    def test_cnetid_filter_limits_changes(self):
        self._run(
            in_wagtail=[
                "teststaff -Old Title- (positionTitle)",
                "someone-else -Old Title- (positionTitle)",
            ],
            in_api=[
                "teststaff -New Title- (positionTitle)",
                "someone-else -Other Title- (positionTitle)",
            ],
            cnetid="teststaff",
        )
        self.staff_page.refresh_from_db()
        self.assertEqual(self.staff_page.position_title, "New Title")
        # someone-else was filtered out — no StaffPage exists for them and no
        # ERROR line should have been printed (no attempt to update them).
