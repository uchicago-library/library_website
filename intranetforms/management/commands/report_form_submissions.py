# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from collections import OrderedDict
import csv
from django.core.management.base import BaseCommand
import hashlib
from io import StringIO
import sys
from wagtail.wagtailcore.models import Page
from wagtail.wagtailforms.models import FormSubmission

class Command (BaseCommand):
    """
    Produce a .csv report from form submissions on the site. 

    Example: 
        python manage.py report_form_submissions /staff/john-jung/contact-john/
    """

    def add_arguments(self, parser):
        """
        Add required positional options and optional
        named arguments.
        """
        # Required positional options
        parser.add_argument('url_path', type=str)

    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement this 
        method. It may return a Unicode string which will be printed to 
        stdout. More: https://docs.djangoproject.com/en/1.8/howto/custom
        -management-commands/#django.core.management.BaseCommand.handle
        """

        try:
            url_path = options['url_path']
            pk = Page.objects.get(url_path='/loop' + url_path).pk
        except:
            sys.exit(1)

        # People may have edited the form over time. The resulting 
        # spreadsheet should group like submissions together. 
        forms = {}
        for s in FormSubmission.objects.filter(page_id=pk):
            # hash the sorted field names for each submission. 
            md5 = hashlib.md5()
            md5.update(''.join(sorted(s.get_data().keys())).encode('utf-8'))
            h = md5.hexdigest()

            # group submissions by hash. 
            if not h in forms:
                forms[h] = []
            forms[h].append(s.get_data())

        output = StringIO()
        csv_writer = csv.writer(output)
        very_first_row = True
        for h in forms:
            first_row = True
            for data in forms[h]:
                sorted_data = sorted(data.items())
                k = list(map(lambda d: str(d[0]).encode('utf-8'), sorted_data))
                v = list(map(lambda d: str(d[1]).encode('utf-8'), sorted_data))
                if first_row:
                    if not very_first_row:
                        csv_writer.writerow([])
                    csv_writer.writerow(k)
                    very_first_row = False
                    first_row = False
                csv_writer.writerow(v)

        # each column gets a question, each row is a set of answers. 
        # put it in a .csv and export. 

        return output.getvalue()
    


