# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from news.models import get_story_summary, NewsPage

import datetime

class Command (BaseCommand):
    """
    Produce a summary of news stories for the day. 

    Example: 
        python manage.py report_daily_news_stories
    """

    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement this 
        method. It may return a Unicode string which will be printed to 
        stdout. More: https://docs.djangoproject.com/en/1.8/howto/custom
        -management-commands/#django.core.management.BaseCommand.handle
        """

        output = []
       
        for news_page in NewsPage.objects.filter(story_date = datetime.date(2016, 3, 7)):
            summary = get_story_summary(news_page)
            output.append(news_page.title)
            output.append(summary['story_date'])
            output.append(summary['title'])
            output.append("https://loop.lib.uchicago.edu/" + summary['url'])
            output.append("By " + summary['author_title'])
            output.append(summary['excerpt'])
            output.append("")

        return "\n".join(output)
    


