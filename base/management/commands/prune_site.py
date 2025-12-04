# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import ast
import socket
import sys

import networkx
from django.core.management.base import BaseCommand
from wagtail.models import Page, Revision

from base.management.commands.get_pages_for_test_db import Command as GetPagesForTestDb


class Command(BaseCommand):
    """
    Prune the site down to something that is appropriate for testing.

    Usage:
        python manage.py prune_site
    """

    G = networkx.DiGraph()

    include_modules = [
        "alerts.models",
        "ask_a_librarian.models",
        "base.models",
        "conferences.models",
        "dirbrowse.models",
        "events.models",
        "findingaids.models",
        "group.models",
        "home.models",
        "intranetforms.models",
        "intranethome.models",
        "intranettocs.models",
        "intranetunits.models",
        "lib_collections.models",
        "news.models",
        "projects.models",
        "public.models",
        "redirects.models",
        "staff.models",
        "subjects.models",
        "units.models",
    ]

    include_fields = {
        "ask_a_librarian.models": {
            "AskPage": [
                "content_specialist",
                "editor",
                "page_maintainer",
                "schedule_appointment_page",
                "visit_page",
            ]
        },
        "base.models": {
            "PublicBasePage": [
                "content_specialist",
                "editor",
                "internal_news_page",
                "page_maintainer",
                "unit",
            ]
        },
        "conferences.models": {
            "ConferencePage": [
                "content_specialist",
                "editor",
                "location" "page_maintainer",
            ]
        },
        "lib_collections.models": {
            "CollectingAreaPage": [
                "collection_location",
                "content_specialist",
                "editor",
                "first_feature",
                "fourth_feature",
                "page_maintainer",
                "second_feature",
                "staff_contact",
                "subject",
                "third_feature",
            ],
            "ExhibitPage": [
                "content_specialist",
                "editor",
                "exhibit_checklist_link_page",
                "exhibit_location",
                "exhibit_text_link_page",
                "page_maintainer",
                "staff_contact",
            ],
        },
        "news.models": {
            "NewsPage": [
                "author",
                "content_specialist",
                "editor",
                "page_maintainer",
            ],
        },
        "public.models": {
            "LocationPage": [
                "content_specialist",
                "editor",
                "page_maintainer",
                "parent_building",
            ],
            "StandardPage": [
                "collection_page",
                "content_specialist",
                "editor",
                "page_maintainer",
            ],
        },
        "staff.models": {
            "StaffPage": [
                "content_specialist",
                "editor",
                "page_maintainer",
                "supervisor_override",
            ]
        },
        "units.models": {
            "UnitPage": [
                "content_specialist",
                "department_head",
                "editor",
                "location",
                "page_maintainer",
                "public_web_page",
            ]
        },
    }

    def get_object_info(self, obj):
        return (type(obj).__module__, type(obj).__name__, obj.pk)

    def get_object_info_tuple(self, obj):
        info = self.get_object_info(obj)
        return ("{}.{}".format(info[0], info[1]), info[2])

    def get_object_from_tuple(self, t):
        try:
            return getattr(
                sys.modules[".".join(t[0].split(".")[:-1])], t[0].split(".").pop()
            ).objects.get(pk=t[1])
        except KeyError:
            print(t)
            sys.exit()

    def add_directories_to_graph(self, obj):
        for o in obj.get_ancestors().specific():
            self.G.add_node(self.get_object_info_tuple(o))
            child = obj
            while True:
                parent = child.get_parent()
                if not parent:
                    break
                self.G.add_edge(
                    self.get_object_info_tuple(child),
                    self.get_object_info_tuple(parent),
                )
                child = parent

    def handle(self, *args, **options):
        directories = True

        related = True

        g = GetPagesForTestDb()
        initial_tuples = ast.literal_eval(g.handle())

        initial_objects = [self.get_object_from_tuple(t) for t in initial_tuples]

        include_subclasses = []
        for m in self.include_fields.keys():
            for c in self.include_fields[m].keys():
                include_subclasses.append(getattr(sys.modules[m], c))
        include_subclasses = tuple(include_subclasses)

        # add initial objects to the system.
        for obj in initial_objects:
            self.G.add_node(self.get_object_info_tuple(obj))
            if directories:
                self.add_directories_to_graph(obj)
            if related:
                for field in obj._meta.fields:
                    related_object = getattr(obj, str(field).split(".").pop())
                    if (
                        not type(related_object).__module__
                        in self.include_fields.keys()
                    ):
                        continue
                    if (
                        not type(related_object).__name__
                        in self.include_fields[type(related_object).__module__]
                    ):
                        continue
                    if not issubclass(type(related_object), include_subclasses):
                        continue
                    self.G.add_edge(
                        self.get_object_info_tuple(obj),
                        self.get_object_info_tuple(related_object),
                    )
                    if directories:
                        self.add_directories_to_graph(related_object)

        save_pages = set()
        for n in self.G.nodes:
            save_pages.add(n)

        all_pages = set()
        for obj in Page.objects.all().specific():
            n = self.get_object_info_tuple(obj)
            all_pages.add(n)

        delete_pages = all_pages - save_pages
        page_revisions = Revision.page_revisions.all()
        revisions_count = page_revisions.count()

        hostname = socket.gethostname()

        if hostname not in ("moss.lib.uchicago.edu", "xibalba.lib.uchicago.edu"):
            print("Development servers only.")
            sys.exit()

        if (
            input(
                "You are about to delete {} pages from {}. {} pages will remain. All {} page revisions will be deleted. Type the name of this server to delete these pages: ".format(
                    len(delete_pages), hostname, len(save_pages), revisions_count
                )
            )
            == hostname
        ):
            objects = [self.get_object_from_tuple(n) for n in delete_pages]
            objects.sort(key=lambda o: o.depth)
            for o in objects:
                try:
                    o.delete()
                except:  # noqa: E722
                    pass
            page_revisions.delete()
            return "{} pages deleted. {}".format(len(delete_pages), revisions_count)
        else:
            return "0 pages deleted."
