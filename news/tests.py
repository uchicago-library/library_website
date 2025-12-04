import datetime

from django.test import TestCase

from news.models import NewsPage


class NewsPageTestCase(TestCase):

    # Load a copy of the production database
    fixtures = ["test.json"]

    def test_news_page_sticky_date(self):
        # when the sticky date is in the future, a sticky story should appear
        # in sticky stories and not in news stories.
        now = datetime.date(2016, 1, 20)
        sticky_story_pks = NewsPage.get_stories(
            sticky=True, now=now
        ).object_list.values_list("pk", flat=True)
        news_story_pks = NewsPage.get_stories(
            sticky=False, now=now
        ).object_list.values_list("pk", flat=True)
        self.assertIn(598, sticky_story_pks)
        self.assertNotIn(598, news_story_pks)

        # when the sticky date is today, a sticky story should appear in sticky
        # stories and not in news stories.
        now = datetime.date(2016, 1, 21)
        sticky_story_pks = NewsPage.get_stories(
            sticky=True, now=now
        ).object_list.values_list("pk", flat=True)
        news_story_pks = NewsPage.get_stories(
            sticky=False, now=now
        ).object_list.values_list("pk", flat=True)
        self.assertIn(598, sticky_story_pks)
        self.assertNotIn(598, news_story_pks)

        # when the sticky date is in the past, a sticky story should not appear
        # in sticky stories but should appear in news stories.
        now = datetime.date(2016, 1, 22)
        sticky_story_pks = NewsPage.get_stories(
            sticky=True, now=now
        ).object_list.values_list("pk", flat=True)
        news_story_pks = NewsPage.get_stories(
            sticky=False, now=now
        ).object_list.values_list("pk", flat=True)
        self.assertNotIn(598, sticky_story_pks)
        self.assertIn(598, news_story_pks)
