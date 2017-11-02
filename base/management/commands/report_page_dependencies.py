# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from django.db import models
from wagtail.wagtailcore.models import Page

import django.apps
import sys

'''
TODO:
    on my staff page right now it doesn't catch my library unit.
'''

class Command (BaseCommand):
    """
    Get the UChicago Library Wagtail dependencies for a page. Dependencies
    include all of the objects that this object points to in the Wagtail admin
    panel. It does not include pages referenced in StreamFields.

    Example: 
        python manage.py report_dependencies staff.models.StaffPage 127
        python manage.py report_dependencies loop.lib.uchicago.edu/staff/john-jung/
    """

    help = 'Get a report of the pages a Wagtail page depends on; e.g. page \
    maintainer, editor, unit, etc.'
     
    skip_fields = [
        'content_type',
        'last_reviewed',
        'owner',
        'page_ptr'
    ]

    include_modules = [
        'alerts.models',
        'ask_a_librarian.models',
        'base.models',
        'conferences.models',
        'dirbrowse.models',
        'events.models',
        'findingaids.models',
        'group.models',
        'home.models',
        'intranetforms.models',
        'intranethome.models',
        'intranettocs.models',
        'intranetunits.models',
        'lib_collections.models',
        'news.models',
        'projects.models',
        'public.models',
        'redirects.models',
        'staff.models',
        'subjects.models',
        'units.models'
    ]

    output_objects = set()

    checked_objects = set()

    def get_object_info(self, obj):
        return (
            obj.__class__.__module__,
            obj.__class__.__name__,
            obj.pk
        )

    def get_object_info_string(self, obj):
        info = self.get_object_info(obj)
        return '{}.{} {}'.format(info[0], info[1], info[2])

    def get_object(self, url):
        '''
        Totally heavy-handed- there's got to be a faster way to do this.
        url: https://loop.lib.uchicago.edu/staff/john-jung/
        '''

        urls = {}
        for page in Page.objects.live():
            if page.url == url:
                return page.specific
        raise ValueError('URL does not exist in Wagtail.')

    def get_related_objects(self, obj):
        '''
        This needs to be able to "go through" through tables.
        '''
        related_objects = set()
        for field in obj._meta.fields:
            field_str = str(field).split('.').pop()
            if field_str in self.skip_fields:
                continue
            # before I checked field.is_relation. 
            related_object = getattr(obj, field_str)
            if not related_object:
                continue
            if not issubclass(type(related_object), models.Model):
                continue
            if not related_object.__class__.__module__ in self.include_modules:
                continue
            related_objects.add(related_object)
        return related_objects

    def get_directories(self, obj):
        try:
            return set(obj.get_ancestors().specific())
        except AttributeError:
            return set()

    def add_dependencies(self, class_module, class_name, primary_key, directories, recursive):
        class_model = getattr(
            sys.modules[class_module],
            class_name
        )
        try:
            o = class_model.objects.get(pk=primary_key)
        except:
            raise ValueError('Object does not exist.')

        while True:
            self.output_objects.add(o)
            self.output_objects = self.output_objects.union(self.get_related_objects(o))
            self.checked_objects.add(o)
            if directories:
                self.output_objects = self.output_objects.union(self.get_directories(o))
            if recursive:
                try:
                    o = next(iter(self.output_objects.difference(self.checked_objects)))
                except StopIteration:
                    break
            else:
                break

    def add_arguments(self, parser):
        """
        Add required positional options and optional
        named arguments.
        """
        # Optional named arguments

        '''
        TODO
        go into the streamfields and get wagtail object dependencies from there too.
        '''
        parser.add_argument(
            '--directories',
            action='store_true',
            default=False,
            help='Include directory hierarchy so pages can live at their original locations.'
        )

        parser.add_argument(
            '--recursive',
            action='store_true',
            default=False,
            help='Follow dependencies.'
        )

        parser.add_argument(
            '--output-wagtail-objects',
            action='store_true',
            default=True,
            help='Output Wagtail classes and primary keys.'
        )

        parser.add_argument(
            '--output-urls',
            action='store_true',
            default=False,
            help='Output URLs, if possible. Otherwise output Wagtail objects.'
        )

        parser.add_argument(
            '--one-of-each',
            action='store_true',
            default=False,
            help='Use a built-in list of pages.'
        )

        # Positional arguments.
        parser.add_argument('arguments', nargs='+')

    def handle(self, *args, **options):
        if len(options['arguments']) == 2:
            # if two positional arguments were passed in, assume they are the
            # object's class and primary key.
            class_name_pieces = options['arguments'][0].split('.')
            class_module = '.'.join(class_name_pieces[:-1])
            class_name = class_name_pieces.pop()
            primary_key = int(options['arguments'][1])
        else:
            # otherwise assume that the argument is a URL to a page. 
            class_module, class_name, primary_key = self.get_object_info(
                self.get_object(options['arguments'][0])
            )

        if options['one_of_each']:
            '''
        alerts.models AlertPage
        alerts.models AlertIndexPage
        ask_a_librarian.models AskPage
        'base.models',
        'conferences.models',
        'dirbrowse.models',
        'events.models',
        'findingaids.models',
        'group.models',
        'home.models',
        'intranetforms.models',
        'intranethome.models',
        'intranettocs.models',
        'intranetunits.models',
        'lib_collections.models',
        'news.models',
        'projects.models',
        'public.models',
        'redirects.models',
        'staff.models',
        'subjects.models',
        'units.models'
    ]
            '''

        else:
            self.add_dependencies(
                class_module,
                class_name,
                primary_key,
                options['directories'], 
                options['recursive']
            )
        return '\n'.join(
            [self.get_object_info_string(o) for o in self.output_objects]
        )
