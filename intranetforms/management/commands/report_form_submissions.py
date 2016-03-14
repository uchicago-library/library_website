# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import csv
from django.core.management.base import BaseCommand
import hashlib
from sys import stdout
from wagtail.wagtailcore.models import Page
from wagtail.wagtailforms.models import FormSubmission

class Command (BaseCommand):
    """
    Produce a .csv report from form submissions on the site. 

    Example: 
        python manage.py report_form_submissions /staff/john-jung/contact-john/
    """

    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement this 
        method. It may return a Unicode string which will be printed to 
        stdout. More: https://docs.djangoproject.com/en/1.8/howto/custom
        -management-commands/#django.core.management.BaseCommand.handle
        """

        output = []

        '''
        # get a url_path from the command line. 
        try:
            pk = Page.object.get(url_path='/loop' + url_path).pk
        except:
            pass

        # People may have edited the form over time. The resulting 
        # spreadsheet should group like submissions together. 
        forms = {}
        for s in FormSubmission.objects.filter(page_id=pk):
            # hash the sorted field names for each submission. 
            md5 = hashlib.md5()
            md5.update(''.join(sorted(s.keys())))
            h = md5.hexdigest()

            # group submissions by hash. 
            if not h in forms:
                forms[h] = []
            forms[h].append(s.get_data())

        csv_writer = csv.writer(stdout)
        very_first_row = True
        for h in forms:
            first_row = True
            for data in forms[h]:
                if first_row:
                    if not very_first_row:
                        csv_writer.writerow([])
                    csv_writer.writerow(sorted(data.keys()))
                    very_first_row = False
                    first_row = False
                csv_writer.writerow(data.values

        # each column gets a question, each row is a set of answers. 
        # put it in a .csv and export. 
        '''

        return "\n".join(output)
    


