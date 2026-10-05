# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys

from django.core.management.base import BaseCommand

from base.models import get_available_path_under, make_slug
from base.utils import get_xml_from_directory_api
from staff.models import StaffIndexPage, StaffPage
from staff.utils import get_individual_info_from_directory


class Command(BaseCommand):
    """
    Report library units that are out of sync between Wagtail and the University Directory.

    Example:
        python manage.py create_or_update_library_staff_page
    """

    def add_arguments(self, parser):
        """
        Add required positional options and optional
        named arguments.
        """
        # Required positional options
        parser.add_argument("cnetid", type=str)

    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement this
        method. It may return a Unicode string which will be printed to
        stdout. More: https://docs.djangoproject.com/en/1.8/howto/custom
        -management-commands/#django.core.management.BaseCommand.handle
        """

        try:
            cnetid = options["cnetid"]
        except KeyError:
            sys.exit(1)

        staff_index_path = StaffIndexPage.objects.first().path
        staff_index_depth = StaffIndexPage.objects.first().depth

        xml_string = get_xml_from_directory_api(
            "https://directory.uchicago.edu/api/v2/individuals/" + cnetid + ".xml"
        )
        info = get_individual_info_from_directory(xml_string)
        next_available_path = get_available_path_under(staff_index_path)

        # Update a StaffPage
        # works with just 'title' set as a default.
        # setting path destroyed the staff index!!!
        # 'path': next_available_path

        if StaffPage.objects.filter(cnetid=info["cnetid"]):
            sp, created = StaffPage.objects.update_or_create(
                cnetid=info["cnetid"],
                defaults={
                    "title": info["displayName"],
                    "display_name": info["displayName"],
                    "official_name": info["officialName"],
                    "slug": make_slug(info["displayName"]),
                    "url_path": "/loop/staff/" + make_slug(info["displayName"]) + "/",
                    "depth": staff_index_depth + 1,
                },
            )
            StaffIndexPage.objects.first().fix_tree(destructive=False)
        else:
            StaffPage.objects.create(
                title=info["displayName"],
                slug=make_slug(info["displayName"]),
                path=next_available_path,
                depth=len(next_available_path) // 4,
                numchild=0,
                url_path="/staff/" + make_slug(info["displayName"]) + "/",
                cnetid=info["cnetid"],
                display_name=info["displayName"],
                official_name=info["officialName"],
            )

        # Add new contact information.
        # for contact_info in info['title_department_subdepartments_dicts']:
        # add new email addresses, phone faculty exchange pairs,
        # telephone numbers.

        # Delete unnecesary contact information.

        staff_page = StaffPage.objects.get(cnetid=info["cnetid"])
        staff_page.page_maintainer = staff_page
        staff_page.save()
