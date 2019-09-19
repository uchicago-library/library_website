import requests
from django.core.management.base import BaseCommand

from .import_news_posts_from_wordpress import API_BASE_URL, WP_SITE_URL

REQUESTS_TIMEOUT = float(3)


def wp_category_url(pnum=''):
    """
    Generate a url to the WordPress categories api.

    Args:
        pnum: string, page number

    Returns:
        string
    """
    if pnum:
        full_url = '{}{}categories/?page={}'.format(
            WP_SITE_URL, API_BASE_URL, pnum
        )
    else:
        full_url = '{}{}categories/'.format(WP_SITE_URL, API_BASE_URL)
    return full_url


class Command(BaseCommand):
    """
    Builds a report that lists the categories currently beings used
    in the news.lib.uchicago.edu WordPress site.

    Args:
        url: string

    Returns:
        None, creates and saves LibNewsPages.
    """
    help = 'Imports news posts from a WordPress blog and saves them in Wagtaill.'

    def handle(self, *args, **options):
        resp = requests.get(wp_category_url(), timeout=REQUESTS_TIMEOUT)
        num_pages = int(resp.headers['X-WP-TotalPages'])
        for page_num in range(1, num_pages + 1):
            wp_cat_page_url = wp_category_url(str(page_num))
            wp_cat_resp = requests.get(
                wp_cat_page_url, timeout=REQUESTS_TIMEOUT
            )
            wp_cat_json = wp_cat_resp.json()
            for cat in wp_cat_json:
                print(cat['name'])
