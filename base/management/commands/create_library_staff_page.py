# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from base.models import get_available_path_under, make_slug
from base.utils import get_xml_from_directory_api
from directory_unit.models import DirectoryUnit
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db import models, migrations
from staff.models import StaffIndexPage, StaffPage, StaffPagePageVCards
from staff.utils import get_individual_info_from_directory

class Command (BaseCommand):
    """
    Report library units that are out of sync between Wagtail and the University Directory.

    Example: 
        python manage.py report_out_of_sync_library_units
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
    
        staff_index_path = StaffIndexPage.objects.first().path
        staff_index_depth = StaffIndexPage.objects.first().depth
        staff_index_url = StaffIndexPage.objects.first().url
        staff_index_content_type_pk = ContentType.objects.get(model='staffindexpage').pk
        staff_content_type_pk = ContentType.objects.get(model='staffpage').pk
    
        info = get_individual_info_from_directory(cnetid)
        next_available_path = get_available_path_under(staff_index_path)

        # This command should create new staff pages only. Add code in the
        # future to update StaffPages. 
        assert not StaffPage.objects.filter(cnetid=cnetid)

        # StaffPage
        StaffPage.objects.create(
        title=info['displayName'],
        slug=make_slug(info['displayName']),
        path=next_available_path,
        depth=len(next_available_path) // 4,
        numchild=0,
        url_path='/staff/' + make_slug(info['displayName']) + '/',
        cnetid=info['cnetid'],
        display_name=info['displayName'],
        official_name=info['officialName'],
        )
   
        # VCards 
        for vcard in info['title_department_subdepartments_dicts']:
            StaffPagePageVCards.objects.create(
            title=vcard['title'],
            unit=DirectoryUnit.objects.get(pk=vcard['department']),
            faculty_exchange=vcard['facultyexchange'],
            email=vcard['email'],
            phone_label='work',
            phone_number=vcard['phone'],
            page=StaffPage.objects.get(cnetid=cnetid)
        )

