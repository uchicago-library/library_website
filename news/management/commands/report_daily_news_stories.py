# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from bs4 import BeautifulSoup
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from news.models import get_story_summary, NewsPage, NewsEmailAddition
from wagtail.wagtailcore.rich_text import expand_db_html

import datetime
import urllib.parse
import re
import smtplib
import sys
import urllib.parse
import textwrap

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
        parser.add_argument('num_days', type=int)
        parser.add_argument('end_date', type=str, nargs='?', default=datetime.datetime.now().strftime('%Y%m%d'))

    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement this 
        method. It may return a Unicode string which will be printed to 
        stdout. More: https://docs.djangoproject.com/en/1.8/howto/custom
        -management-commands/#django.core.management.BaseCommand.handle
        """

        num_days = options['num_days']

        try:
            end_date = datetime.datetime.strptime(options['end_date'], '%Y%m%d')
        except ValueError:
            raise CommandError('Please enter dates in yyyymmdd format.')

        # get relevant news stories.
        news_stories = NewsPage.objects.live().filter(story_date__range=(end_date - datetime.timedelta(days=num_days), end_date))

        # if there were no news stories, just exit. 
        if news_stories.count() == 0:
            return 'No news stories during that time period.'

        def clean_html(html):
            html = html.replace("<p></p>", "")
            html = html.replace("<p><br/></p>", "")
            html = html.replace("<br/><li>", "<li>")
            html = html.replace("<br/></li>", "</li>")
            html = html.replace("<br/><p>", "<p>")
            html = html.replace("<br/></p>", "</p>")
            return html

        # build html first, then convert that html to text for the text part of the email.  
        def get_html(news_stories, additional_link_params, header_html, extra_html, footer_html):
            html = "<html><head></head><body>" + header_html
            html = html + "<ul>"
            for news_story in news_stories.order_by('-story_date'):
                url = 'https://loop.lib.uchicago.edu' + news_story.url_path.replace('/loop', '', 1) + '?' + urllib.parse.urlencode(additional_link_params)
                html = html + "<li><a href='" + url + "'>"
                html = html + news_story.title 
                html = html + "</a></li>"
            html = html + "</ul>"
            html = html + extra_html
            html = html + footer_html
            html = html + "</body></html>"

            # rough pass to clean strangely nested elements.
            soup = BeautifulSoup(html, "lxml")

            # do more cleanup work. 
            html = clean_html(str(soup))

            # get the real links for things like documents and internal pages. 
            html = expand_db_html(html)

            return html

        # convert html to text. 
        def html_to_text(html):
            # replace the easy stuff. 
            replacements = {
                "<br>": "\n",
                "<br/>": "\n",
                "</h2>": "\n\n",
                "</h3>": "\n\n",
                "</h4>": "\n\n",
                "</h5>": "\n\n",
                "<li>": "  *   ",
                "</li>": "\n",
                "</ol>": "\n",
                "</p>": "\n\n",
                "</ul>": "\n"
            }
            replacements = dict((re.escape(k), v) for k, v in replacements.items())
            pattern = re.compile("|".join(replacements.keys()))
            html = pattern.sub(lambda m: replacements[re.escape(m.group(0))], html) 

            # re-arrange links. 
            # insert placeholder characters to make it easier to remove all remaining tags.
            pattern = re.compile("<a.*?href=['\"](.*?)['\"].*?>(.*?)</a>", re.DOTALL|re.MULTILINE)
            html = pattern.sub(r"\2 :::::jej:::::\1;;;;;jej;;;;;", html)

            # remove all remaining tags.
            pattern = re.compile("<.*?>", re.DOTALL|re.MULTILINE)
            html = pattern.sub("", html)

            # replace placeholder charaters with angle brackets. 
            html = html.replace(':::::jej:::::', '<')
            html = html.replace(';;;;;jej;;;;;', '>')

            return html

        output = []

        # params to attach to links. 
        additional_link_params = {
            'utm_campaign': end_date.strftime('%Y%m%d'),
            'utm_medium': 'email',
            'utm_source': 'loop_email_digest'
        }

        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Loop digest for ' + end_date.strftime('%B %-d, %Y')
        msg['From'] = 'jej@uchicago.edu'
        msg['To'] = 'jej@uchicago.edu'

        # there must be zero or one headers. If not this will error out. 
        try:
            header_html = NewsEmailAddition.objects.get(is_header=True).text
        except ObjectDoesNotExist:
            header_html = ''

        # there must be zero or one footers. If not this will error out. 
        try:
            footer_html = NewsEmailAddition.objects.get(is_footer=True).text
        except ObjectDoesNotExist:
            footer_html = ''

        # get extra html for this email, if it exists.
        extra_html = ''.join(NewsEmailAddition.objects.filter(include_in_email_dated=end_date).values_list('text', flat=True))
  
        # build the html version of the email. 
        html = get_html(news_stories, additional_link_params, header_html, extra_html, footer_html)

        # get a text version from that.
        text = html_to_text(html)

        # attach all the parts to the email and mail it. 
        part1 = MIMEText(text, 'plain')
        msg.attach(part1)
        part2 = MIMEText("\n".join(textwrap.wrap(html, break_long_words=False, width=70)), 'html')
        msg.attach(part2)

        s = smtplib.SMTP('localhost')
        s.send_message(msg)
        s.quit()

        return 'Message sent.'
    


