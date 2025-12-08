import logging

from django.contrib import messages
from django.contrib.auth.models import Permission, User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import re_path, reverse
from wagtail import hooks
from wagtail.admin.menu import MenuItem

from base.utils import save_virtual_workbook
from public.models import StaffPublicPage
from staff.models import StaffPage
from staff.utils import WagtailStaffReport

logger = logging.getLogger(__name__)


def admin_view(request):
    from staff.forms import StaffReportingForm

    if request.method == "POST":
        form = StaffReportingForm(request.POST)
        options = {
            "filename": form.data.get("filename", "staff_report"),
            "cnetid": form.data.get("cnetid", None),
            "department": form.data.get("department", None),
            "department_and_subdepartments": form.data.get(
                "department_and_subdepartments", None
            ),
            "group": form.data.get("group", None),
            "live": form.data.get("live", None),
            "latest_revision_created_at": form.data.get(
                "latest_revision_created_at", None
            ),
            "position_eliminated": form.data.get("position_eliminated", None),
            "supervises_students": form.data.get("supervises_students", False),
            "supervisor_cnetid": form.data.get("supervisor_cnetid", None),
            "supervisor_override": form.data.get("supervisor_override", None),
            "position_title": form.data.get("position_title", None),
        }

        for i in ("live", "supervises_students", "supervisor_override"):
            try:
                if options[i]:
                    options[i] = True
            except KeyError:
                continue
        options["all"] = not (bool(options["live"]))

        if form.is_valid():
            staff_report = WagtailStaffReport(
                sync_report=False, staff_report=True, **options
            )
            virtual_workbook = save_virtual_workbook(staff_report.workbook())
            response = HttpResponse(
                virtual_workbook,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response["content-disposition"] = (
                'attachment; filename="' + options["filename"] + '.xlsx"'
            )
            return response
        else:
            return render(request, "staff/staff_reporting_form.html", {"form": form})
    else:
        form = StaffReportingForm({"live": True, "filename": "staff_report"})
    return render(request, "staff/staff_reporting_form.html", {"form": form})


@hooks.register("register_admin_urls")
def urlconf_time():
    return [re_path(r"^list_staff_wagtail/$", admin_view, name="list_staff_wagtail")]


@hooks.register("register_settings_menu_item")
def register_frank_menu_item():
    return MenuItem(
        "Staff Reporting",
        reverse("list_staff_wagtail"),
        classname="icon icon-mail",
        order=9990,
    )


@hooks.register("register_permissions")
def register_staff_hr_permission():
    """
    Register the custom staff HR permission so it appears
    in the Wagtail Groups administration interface.
    """
    return Permission.objects.filter(
        content_type__app_label="staff", codename="change_staff_hr_info"
    )


@hooks.register("before_edit_user")
def show_user_edit_help(request, user):
    """
    Display an info message on the user edit form explaining the automatic
    staff page publishing/unpublishing behavior.
    """
    messages.info(
        request,
        "Note: Marking a user as inactive will automatically unpublish their staff pages (both Loop and public). "
        "Reactivating will republish them. This only works when editing individual users, not with bulk actions.",
    )


@receiver(post_save, sender=User)
def manage_staff_pages_on_user_active_state_change(sender, instance, **kwargs):
    """
    Automatically unpublish staff pages when a user is marked inactive,
    and republish them when a user is reactivated.
    The username matches the cnetid field on both StaffPage and StaffPublicPage.

    Note: This only works when editing individual users through the admin interface.
    The bulk "Set active state" action does not trigger this signal, so users must be
    activated/deactivated individually to automatically publish/unpublish their staff pages.
    """
    if not instance.is_active:
        # Unpublish Loop staff page(s)
        for staff_page in StaffPage.objects.filter(cnetid=instance.username, live=True):
            try:
                staff_page.unpublish()
            except Exception as e:
                logger.warning(
                    f"Failed to unpublish StaffPage for {instance.username}: {e}"
                )

        # Unpublish public staff page(s)
        for public_page in StaffPublicPage.objects.filter(
            cnetid=instance.username, live=True
        ):
            try:
                public_page.unpublish()
            except Exception as e:
                logger.warning(
                    f"Failed to unpublish StaffPublicPage for {instance.username}: {e}"
                )
    else:
        # User is active - republish their staff pages if they exist and are unpublished
        # Publish Loop staff page(s)
        for staff_page in StaffPage.objects.filter(
            cnetid=instance.username, live=False
        ):
            try:
                staff_page.save_revision().publish()
            except Exception as e:
                logger.warning(
                    f"Failed to publish StaffPage for {instance.username}: {e}"
                )

        # Publish public staff page(s)
        for public_page in StaffPublicPage.objects.filter(
            cnetid=instance.username, live=False
        ):
            try:
                public_page.save_revision().publish()
            except Exception as e:
                logger.warning(
                    f"Failed to publish StaffPublicPage for {instance.username}: {e}"
                )
