# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from subjects.models import Subject

def get_children(subject):
    return list(Subject.objects.filter(parent_subject__parent=subject))

def name(subject):
    n = subject.name
    if subject.parent_subject.count() > 1:
        n = n + ' *'
    return n

class Command (BaseCommand):
    """
    Make a report of subjects.

    Example: 
        python manage.py report_subjects
    """

    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement this 
        method. It may return a Unicode string which will be printed to 
        stdout. More: https://docs.djangoproject.com/en/1.8/howto/custom
        -management-commands/#django.core.management.BaseCommand.handle
        """

        text_only = False

        output = []

        if text_only:
            for a in Subject.objects.filter(parent_subject=None):
                output.append(name(a)) 
                for b in get_children(a):
                    output.append(" - ".join([name(a), name(b)]))
                    for c in get_children(b):
                        output.append(" - ".join([name(a), name(b), name(c)]))
                        for d in get_children(c):
                            output.append(" - ".join([name(a), name(b), name(c), name(d)]))
                            for e in get_children(d):
                                output.append(" - ".join([name(a), name(b), name(c), name(d), name(e)]))
                                for f in get_children(e):
                                    output.append(" - ".join([name(a), name(b), name(c), name(d), name(e), name(f)]))
                                    for g in get_children(f):
                                        raise Exception('Not enough iterative loops!')
        else:
            output.append("<html><body><ul>")
            for a in Subject.objects.filter(parent_subject=None):
                output.append("<li>" + name(a)) 
                output.append("<ul>")
                for b in get_children(a):
                    output.append("<li>" + name(b)) 
                    output.append("<ul>")
                    for c in get_children(b):
                        output.append("<li>" + name(c)) 
                        output.append("<ul>")
                        for d in get_children(c):
                            output.append("<li>" + name(d)) 
                            output.append("<ul>")
                            for e in get_children(d):
                                output.append("<li>" + name(e)) 
                                output.append("<ul>")
                                for f in get_children(e):
                                    output.append("<li>" + name(f)) 
                                    for g in get_children(f):
                                        raise Exception('Not enough iterative loops!')
                                    output.append("</li>")
                                output.append("</ul>")
                                output.append("</li>")
                            output.append("</ul>")
                            output.append("</li>")
                        output.append("</ul>")
                        output.append("</li>")
                    output.append("</ul>")
                    output.append("</li>")
                output.append("</ul>")
                output.append("</li>")
            output.append("</ul></body><p>* indicates a subject with more than one parent.</p></html>")

        return "\n".join(output)

