# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand

import base64
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'library_website.settings'
import sys

from base.models import get_available_path_under
from group.models import GroupMeetingMinutesIndexPage, GroupMeetingMinutesPage, GroupPage, GroupReportsIndexPage, GroupReportsPage
from intranetunits.models import IntranetUnitsPage, IntranetUnitsReportsIndexPage, IntranetUnitsReportsPage
from http.client import HTTPSConnection
from xml.etree import ElementTree

try:
    from library_website.settings import DIRECTORY_USERNAME, DIRECTORY_PASSWORD
except(ImportError):
    import os
    DIRECTORY_USERNAME = os.environ['DIRECTORY_USERNAME']
    DIRECTORY_PASSWORD = os.environ['DIRECTORY_PASSWORD']

class Command (BaseCommand):
    """
    Report library units that are out of sync between Wagtail and the University Directory.

    Example: 
        python manage.py make_meeting_minutes_and_reports_pages
    """
    def add_arguments(self, parser):
        """
        Add required positional options and optional
        named arguments.
        """
        # Required positional options
        parser.add_argument('path', type=str)

    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement this 
        method. It may return a Unicode string which will be printed to 
        stdout. More: https://docs.djangoproject.com/en/1.8/howto/custom
        -management-commands/#django.core.management.BaseCommand.handle
        """

        # Convenience variables for required fields.
        # Save in a dict so we can pass an unspecified
        # numer or arguments to the get_or_create method.
        try:
            kwargs = {
                'path': options['path']
            }
        except:
            sys.exit(1)

        # Make sure the path begins and ends with a slash.
        if not kwargs['path'][0] == '/':
            kwargs['path'] = '/' + kwargs['path']

        if not kwargs['path'][-1] == '/':
            kwargs['path'] = kwargs['path'] + '/'

        # GROUP PAGES
        if '/groups/' in kwargs['path']:
            # MEETING MINUTES
            try:
                group_page = GroupPage.objects.get(url_path='/loop' + kwargs['path'])
                group_meeting_minutes_page = GroupMeetingMinutesPage.objects.descendant_of(group_page).get()
            except:
                return "The group page could not be found."
    
            if GroupMeetingMinutesIndexPage.objects.descendant_of(group_page).count() == 0:
                group_meeting_minutes_page.title = '2016'
                group_meeting_minutes_page.slug = '2016'
                group_meeting_minutes_page.set_url_path(group_page)
                group_meeting_minutes_page.save()
        
                # Create a new group meeting minutes index page. 
                group_meeting_minutes_index_page = GroupMeetingMinutesIndexPage.objects.create(
                    depth=group_page.depth + 1,
                    numchild=0,
                    path=get_available_path_under(group_page.path),
                    slug='meeting-minutes',
                    title='Meeting Minutes',
                    url_path='/loop' + kwargs['path'] + 'meeting-minutes/'
                )
           
                group_meeting_minutes_page.move(group_meeting_minutes_index_page, 'first-child')
    
            # GROUP REPORTS
            try:
                group_reports_page = GroupReportsPage.objects.descendant_of(group_page).get()
            except:
                return "The group page could not be found."
    
            if GroupReportsIndexPage.objects.descendant_of(group_page).count() == 0:
                group_reports_page.title = '2016'
                group_reports_page.slug = '2016'
                group_reports_page.set_url_path(group_page)
                group_reports_page.save()
        
                # create a group reports index page here- call it "Reports".
                group_reports_index_page = GroupReportsIndexPage.objects.create(
                    depth=group_page.depth + 1,
                    numchild=0,
                    path=get_available_path_under(group_page.path),
                    slug='reports',
                    title='Reports',
                    url_path='/loop' + kwargs['path'] + 'reports/'
                )
        
                # move 2016 into "Reports".
                group_reports_page.move(group_reports_index_page, 'first-child')
    
            # fix paths.
            group_page.fix_tree(destructive=False)

        # DEPARTMENT PAGES
        elif '/departments/' in kwargs['path']:
            try:
                department_page = IntranetUnitsPage.objects.get(url_path='/loop' + kwargs['path'])
                department_reports_page = IntranetUnitsReportsPage.objects.child_of(department_page).get()
            except:
                return "The department page could not be found."

            if IntranetUnitsReportsIndexPage.objects.child_of(department_page).count() == 0:
                department_reports_page.title = '2016'
                department_reports_page.slug = '2016'
                department_reports_page.set_url_path(department_page)
                department_reports_page.save()

                # create a department reports index page here- call it "Reports".
                department_reports_index_page = IntranetUnitsReportsIndexPage.objects.create(
                    depth=department_page.depth + 1,
                    numchild=0,
                    path=get_available_path_under(department_page.path),
                    slug='reports',
                    title='Reports',
                    url_path='/loop' + kwargs['path'] + 'reports/'
                )

                # move 2016 into "Reports".
                department_reports_page.move(department_reports_index_page, 'first-child')
    
                # fix paths.
                department_page.fix_tree(destructive=False)

        return "SUCCESS: " + kwargs['path']


