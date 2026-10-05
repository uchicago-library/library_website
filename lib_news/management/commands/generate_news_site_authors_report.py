import requests
from django.core.management.base import BaseCommand

WP_SITE_URL = "http://news.lib.uchicago.edu"
REQUESTS_TIMEOUT = float(3)
POSTS_PER_PAGE = 100
START_PAGE = 1
API_BASE_URL = "/wp-json/wp/v2/"


def wp_users_url(page_num):
    """
    Generate a url to the WordPress posts api.

    Args:
        page_num: int, page number to parse

    Returns:
        string
    """
    full_url = "{}{}users/?per_page={}&page={}".format(
        WP_SITE_URL, API_BASE_URL, str(POSTS_PER_PAGE), str(START_PAGE)
    )
    return full_url


class Command(BaseCommand):
    """
    Imports WordPress posts from our news site into Wagtail.

    Args:
        url: string

    Returns:
        None, creates and saves LibNewsPages.
    """

    help = "Imports news posts from a WordPress blog and saves them in Wagtaill."

    def handle(self, *args, **options):
        wp_authors_url = wp_users_url(START_PAGE)
        resp = requests.get(wp_authors_url, timeout=REQUESTS_TIMEOUT)
        num_pages = int(resp.headers["X-WP-TotalPages"])
        for page_num in range(1, num_pages + 1):
            wp_author_page_url = wp_users_url(str(page_num))
            wp_author_resp = requests.get(wp_author_page_url, timeout=REQUESTS_TIMEOUT)
            wp_author_json = wp_author_resp.json()
            for author in wp_author_json:
                print(author["name"])
