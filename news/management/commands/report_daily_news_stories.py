# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from news.models import get_story_summary, NewsPage

import datetime
import re
import sys

# followed first example here:
# https://docs.python.org/3/library/email-examples.html
# tried to send email from and to jej at 4:55pm. 

class Command (BaseCommand):
    """
    Produce a summary of news stories for a given day.

    Example: 
        python manage.py report_daily_news_stories yyyymmdd number-of-days
    """

    def add_arguments(self, parser):
        """
        Add required positional options and optional
        named arguments.
        """
        # Required positional options
        parser.add_argument('start_date', type=str)
        parser.add_argument('num_days', type=int)

    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement this 
        method. It may return a Unicode string which will be printed to 
        stdout. More: https://docs.djangoproject.com/en/1.8/howto/custom
        -management-commands/#django.core.management.BaseCommand.handle
        """

        try:
            start_year = int(options['start_date'][:4])
            start_month = int(options['start_date'][4:-2])
            start_day = int(options['start_date'][6:])
            start_date = datetime.date(start_year, start_month, start_day)
            num_days = options['num_days']
            print(num_days)

        except:
            sys.exit(1)

        output = []

        # campaign is always the current day: e.g. 20160901
        utm_campaign = datetime.datetime.now().strftime('%Y%m%d')
        utm_medium = 'email'
        utm_source = 'loop_email_digest'

        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Loop digest for Monday, August 29'
        msg['From'] = 'eee@uchicago.edu'
        msg['To'] = 'jej@uchicago.edu'
   
        text = "Here is a round-up of some interesting Loop news stories that "
        text = text + "you may have missed.\n"
        for d in [start_date + datetime.timedelta(days=x) for x in range(num_days, -1, -1)]:
            for news_page in NewsPage.objects.filter(story_date = d):
                text = text + "  *   "
                text = text + news_page.title
                text = text + "<"
                text = text + "https://loop.lib.uchicago.edu" + news_page.url_path.replace('/loop', '', 1)
                text = text + ">\n"

        text = text + "\n"
        text = text + "As always, contact"
        text = text + "intranet@lib.uchicago.edu"
        text = text + "<mailto:intranet@lib.uchicago.edu> "
        text = text + "with any questions or feedback regarding Loop.\n"
        text = text + "Thanks,\n"
        text = text + "Elizabeth\n"
        text = text + "On behalf of the Intranet Advisory Group\n\n"
        text = text + "Elizabeth Edwards\n"
        text = text + "Assessment Librarian\n"
        text = text + "University of Chicago Library\n"
        text = text + "773-834-8972\n"
        text = text + "eee@uchicago.edu<mailto:eee@uchicago.edu>\n"

        part1 = MIMEText(text, 'plain')
        msg.attach(part1)

        html = "<html><head></head><body>Here is a round-up of some"
        html = html + "interesting Loop news stories that you may have"
        html = html + " missed<br><ul>"
        for d in [start_date + datetime.timedelta(days=x) for x in range(num_days, -1, -1)]:
            for news_page in NewsPage.objects.filter(story_date = d):
                html = html + "<li><a href='" + news_page.url_path.replace('/loop', '', 1) + "'>"
                html = html + news_page.title + "</a></li>"
        html = html + "</ul>"
        html = html + "<p>As always, contact <a "
        html = html + "href='mailto:intranet@lib.uchicago.edu'>"
        html = html + "intranet@lib.uchicago.edu</a> with any "
        html = html + "questions or feedback regarding "
        html = html + "Loop.<br>Thanks,<br>Elizabeth<br>On behalf of "
        html = html + "the Intranet Advisory Group</p>"
        html = html + "<p>Elizabeth Edwards<br>Assessment "
        html = html + "Librarian<br>University of Chicago "
        html = html + "Library<br>773-834-8972<br><a href='mailto:"
        html = html + "eee@uchicago.edu'>eee@uchicago.edu</a></p>"

        part2 = MIMEText(html, 'html')
        msg.attach(part2)

        return msg.as_string()
    


