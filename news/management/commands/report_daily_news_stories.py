# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from news.models import get_story_summary, NewsPage

import datetime

class Command (BaseCommand):
    """
    Produce a summary of news stories for a given day.

    Example: 
        python manage.py report_daily_news_stories yyyy m d
    """

    def add_arguments(self, parser):
        """
        Add required positional options and optional
        named arguments.
        """
        # Required positional options
        parser.add_argument('year', type=int)
        parser.add_argument('month', type=int)
        parser.add_argument('day', type=int)

    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement this 
        method. It may return a Unicode string which will be printed to 
        stdout. More: https://docs.djangoproject.com/en/1.8/howto/custom
        -management-commands/#django.core.management.BaseCommand.handle
        """

        try:
            year = options['year']
            month = options['month']
            day = options['day']

        except:
            sys.exit(1)

        output = []
      
        for news_page in NewsPage.objects.filter(story_date = datetime.date(year, month, day)):
            summary = get_story_summary(news_page)
            output.append(news_page.title)
            output.append(summary['story_date'])
            output.append(summary['title'])
            output.append("https://loop.lib.uchicago.edu/" + summary['url'])
            output.append("By " + summary['author_title'])
            output.append(summary['excerpt'])
            output.append("")

        return "\n".join(output)
    


