# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from news.utils import send_loop_news_email_notifications
from django.core.management.base import BaseCommand

import datetime

# if there were no new Loop news stories, do nothing.

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
        parser.add_argument('from_email', type=str)
        parser.add_argument('to_email', type=str)
        parser.add_argument('num_days', type=int)
        parser.add_argument('end_date', type=str, nargs='?', default=datetime.datetime.now().strftime('%Y%m%d'))

    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement this 
        method. It may return a Unicode string which will be printed to 
        stdout. More: https://docs.djangoproject.com/en/1.8/howto/custom
        -management-commands/#django.core.management.BaseCommand.handle
        """

        from_email = options['from_email']
        to_email = options['to_email']
        num_days = options['num_days']
        end_date = options['end_date']

        r = send_loop_news_email_notifications(from_email, to_email, num_days, end_date)
        if r:
            return 'Message sent.'
    


