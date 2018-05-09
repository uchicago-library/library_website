# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from subjects.models import Subject

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
            for a in Subject.get_top_level_subjects().order_by('name'):
                output.append(name(a)) 
                for b in a.get_children():
                    output.append(" - ".join([name(a), name(b)]))
                    for c in b.get_children():
                        output.append(" - ".join([name(a), name(b), name(c)]))
                        for d in c.get_children():
                            output.append(" - ".join([name(a), name(b), name(c), name(d)]))
                            for e in d.get_children():
                                output.append(" - ".join([name(a), name(b), name(c), name(d), name(e)]))
                                for f in e.get_children():
                                    output.append(" - ".join([name(a), name(b), name(c), name(d), name(e), name(f)]))
                                    for g in f.get_children():
                                        raise Exception('Not enough iterative loops!')
        else:
            output.append("<html><body><ul>")
            for a in Subject.get_top_level_subjects().order_by('name'):
                output.append("<li><a href='/collex/?view=subjects#" + a.name + "'>" + name(a) + "</a>") 
                output.append("<ul>")
                for b in a.get_children():
                    output.append("<li><a href='/collex/?view=subjects#" + b.name + "'>" + name(b) + "</a>") 
                    output.append("<ul>")
                    for c in b.get_children():
                        output.append("<li><a href='/collex/?view=subjects#" + c.name + "'>" + name(c) + "</a>") 
                        output.append("<ul>")
                        for d in c.get_children():
                            output.append("<li><a href='/collex/?view=subjects#" + d.name + "'>" + name(d) + "</a>") 
                            output.append("<ul>")
                            for e in d.get_children():
                                output.append("<li><a href='/collex/?view=subjects#" + e.name + "'>" + name(e) + "</a>") 
                                output.append("<ul>")
                                for f in e.get_children():
                                    output.append("<li><a href='/collex/?view=subjects#" + f.name + "'>" + name(f) + "</a>") 
                                    for g in f.get_children():
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

