import json
import sys
from io import BytesIO

import pytz
import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse
from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand
from lib_news.models import (
    LibNewsIndexPage, LibNewsPage, LibNewsPageCategories, PublicNewsCategories
)
from staff.models import StaffPage
from units.models import UnitPage
from wagtail.images.models import Image

WP_SITE_URL = 'http://news.lib.uchicago.edu'
REQUESTS_TIMEOUT = float(10)
POSTS_PER_PAGE = 10
START_PAGE = 1
API_BASE_URL = '/wp-json/wp/v2/'
STAFF_ID = 223
UNIT_ID = 2455


def map_cat(name):
    """
    Wrapper function for PublicNewsCategories snippet
    get method.

    Args:
        name: string, category name

    Returns:
        PublicNewsCategories object.
    """
    return LibNewsPageCategories(
        category=PublicNewsCategories.objects.get(text=name)
    )


CAT_MAP = {
    'Feature Story': map_cat('Klingons'),
    'Law': map_cat('Borg'),
    'New Acquisitions': map_cat('Picard'),
    'Resources': map_cat('DS9'),
}


def get_cats(wp_cats):
    """
    Get a list of categories translated from WordPress.

    Args:
        wp_cats: list of strings, category names.

    Returns:
        list of LibNewsPageCategories.
    """
    meow = []
    for cat in wp_cats:
        if cat in CAT_MAP:
            meow.append(CAT_MAP[cat])
    return meow


def wp_posts_url(site_url, ppp, pnum):
    """
    Generate a url to the WordPress posts api.

    Args:
        site_url: string
        ppp: string, number of posts per page
        pnum: string, page number to get

    Returns:
        string
    """
    full_url = '{}{}posts?per_page={}&page={}'.format(
        site_url, API_BASE_URL, str(ppp), str(pnum)
    )
    return full_url


def wp_user_url(uid):
    """
    Generate a url to the WordPress posts api.

    Args:
        uid: string, user id

    Returns:
        string
    """
    full_url = '{}{}users/{}'.format(WP_SITE_URL, API_BASE_URL, uid)
    return full_url


def wp_category_url(cid):
    """
    Generate a url to the WordPress categories api.

    Args:
        cid: string, category id

    Returns:
        string
    """
    full_url = '{}{}categories/{}'.format(WP_SITE_URL, API_BASE_URL, cid)
    return full_url


def wp_media_url(mid):
    """
    Generate a url to the WordPress media api.

    Args:
        mid: string, media id

    Returns:
        string
    """
    full_url = '{}{}media/{}'.format(WP_SITE_URL, API_BASE_URL, mid)
    return full_url


def get_wp_post_author(wp_post):
    """
    Get the author of a WordPress post or a custom author byline
    if it exists.

    Args:
        wp_post: json data representing a single WordPress post.

    Returns:
        string, author name
    """
    wp_author_id = wp_post['author']
    wp_author_url = wp_user_url(wp_author_id)
    wp_author_resp = requests.get(wp_author_url, timeout=REQUESTS_TIMEOUT)
    wp_author_json = wp_author_resp.json()
    wp_author_name = wp_author_json['name']
    wp_custom_author_byline = wp_post['custom_author_byline']
    if wp_custom_author_byline:
        return wp_custom_author_byline
    return wp_author_name


def get_image(media_url):
    """
    Wrapper function for requests.get.

    Args:
        media: string, url

    Returns:
        Request response
    """
    print('Getting image')
    return requests.get(media_url, timeout=REQUESTS_TIMEOUT)


def get_wp_media_data(iid):
    """
    Get information about a WordPress media file.

    Args:
        iid: int, image id

    Returns:
        tuple, data about an image file.
    """
    wp_media_resp = get_image(wp_media_url(iid))
    wp_media_json = wp_media_resp.json()
    wp_media_title = wp_media_json['title']['rendered']
    wp_media_filename = wp_media_json['media_details']['sizes']['full']['file']
    wp_media_caption = wp_media_json['caption']['rendered']
    return (
        wp_media_title, wp_media_json['source_url'], wp_media_filename,
        wp_media_caption
    )


def get_wp_post_categories(wp_post):
    """
    Get categories for a WordPress post.

    Args:
        wp_post: json data representing a single WordPress post.

    Returns:
        list of strings, category names
    """
    wp_category_ids = wp_post['categories']
    cats = []
    for wp_cat_id in wp_category_ids:
        wp_cat_url = wp_category_url(wp_cat_id)
        wp_cat_resp = requests.get(wp_cat_url, timeout=REQUESTS_TIMEOUT)
        wp_cat_json = wp_cat_resp.json()
        wp_cat_name = wp_cat_json['name']
        cats.append(wp_cat_name)
    return cats


def get_wp_post_data(wp_post_json):
    """
    Get data related to a WordPress post.

    Args:
        wp_post_json: json from WordPres posts api.

    Returns:
        dictionary of data about the post, mixed.
    """
    wp_author = get_wp_post_author(wp_post_json)
    wp_categories = get_wp_post_categories(wp_post_json)
    wp_fm_id = wp_post_json['featured_media']
    wp_fm_title = ''
    wp_fm_url = ''
    wp_fm_filename = ''
    wp_fm_caption = ''
    if wp_fm_id > 0:
        wp_fm_title, wp_fm_url, wp_fm_filename, wp_fm_caption = get_wp_media_data(
            wp_fm_id
        )

    return {
        'title': wp_post_json['title']['rendered'],
        'author': wp_author,
        'categories': wp_categories,
        'featured_media_id': wp_post_json['featured_media'],
        'featured_media_title': wp_fm_title,
        'featured_media_url': wp_fm_url,
        'featured_media_filename': wp_fm_filename,
        'featured_media_caption': wp_fm_caption,
        'published_at': pytz.utc.localize(parse(wp_post_json['date'])),
        'content': wp_post_json['content']['rendered'],
        'excerpt': wp_post_json['excerpt']['rendered'],
    }


def map_img_alignment_class(css):
    """
    Takes css applied to WordPress images and maps the
    alignment classes to the corresponding classes in
    wordpress.

    Args:
        css: list of css classes applied to the image.

    Returns:
        string, Wagtail image streamfield css alignment
        classname.
    """
    if 'size-full' in css:
        return 'fullwidth'
    elif 'alignright' in css:
        return 'pull-right'
    else:
        return 'pull-left'


def toggle_img_alignment_class(classname):
    """
    Toggles the alignment class between align left
    and align right for image streamfield blocks.
    Used when there are multiple images in a story.

    Returns:
        string, css class.
    """
    al = 'pull-left'
    ar = 'pull-right'
    css = {al: ar, ar: al}
    return css[classname]


def clean_excerpt(excerpt):
    """
    Strip out the nasty Continue Reading link text from WordPress.

    Args:
        excerpt: string, html

    Returns:
        string, html
    """
    soup = BeautifulSoup(excerpt, 'html5lib')
    soup.find('span', class_='meta-nav').parent.decompose()
    return soup


class Command(BaseCommand):
    """
    Imports WordPress posts from our news site into Wagtail.

    Args:
        url: string

    Returns:
        None, creates and saves LibNewsPages.
    """
    help = 'Imports news posts from a WordPress blog and saves them in Wagtaill.'

    def add_arguments(self, parser):
        """
        Get required positional options and optional
        named arguments.
        """
        # Required positional options
        parser.add_argument('pid', nargs='+', type=int)

    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement this
        method. It may return a Unicode string which will be printed to
        stdout. More: https://docs.djangoproject.com/en/1.8/howto/custom
        -management-commands/#django.core.management.BaseCommand.handle
        """
        pid = options['pid'][0]
        try:
            news_index_page = LibNewsIndexPage.objects.get(id=pid)
        except (LibNewsIndexPage.DoesNotExist):
            print(
                'A LibNewsIndexPage with ID {} does not exist'.format(str(pid))
            )
            sys.exit()

        unit = UnitPage.objects.get(id=UNIT_ID)
        staff = StaffPage.objects.get(id=STAFF_ID)

        # TODO - setup logging of failures
        # TODO - write commands for getting all categories and author names for mapping purposes
        # posts_url = wp_posts_url(base_url, str(POSTS_PER_PAGE), str(START_PAGE))
        # resp = requests.get(posts_url, timeout=REQUESTS_TIMEOUT)
        # num_pages = resp.headers['X-WP-TotalPages']
        num_pages = 1
        for page_num in range(1, num_pages + 1):
            print(
                'Importing posts from page {} of {}'.format(
                    page_num, num_pages
                )
            )
            print('==================================')
            posts_page_url = wp_posts_url(
                WP_SITE_URL, str(POSTS_PER_PAGE), page_num
            )
            pp_resp = requests.get(posts_page_url, timeout=REQUESTS_TIMEOUT)
            pp_json = pp_resp.json()
            for wp_post in pp_json:
                # General WordPress data regarding the current post
                wp_post_data = get_wp_post_data(wp_post)
                wp_post_title = wp_post_data['title']
                wp_author_name = wp_post_data['author']
                wp_categories = wp_post_data['categories']
                wp_fm_title = wp_post_data['featured_media_title']
                wp_fm_url = wp_post_data['featured_media_url']
                wp_fm_filename = wp_post_data['featured_media_filename']
                wp_post_published_at = wp_post_data['published_at']
                wp_post_content = wp_post_data['content']
                wp_post_excerpt = clean_excerpt(wp_post_data['excerpt'])

                # Skip Alerts
                if 'Alert' in wp_categories:
                    continue

                # Temporary
                if wp_fm_title and wp_fm_url:
                    # List of categories for Wagtail
                    cats = get_cats(wp_categories)

                    # Get the thumbnail and build an entry for Wagtail
                    img_response = get_image(wp_fm_url)
                    thumbnail = Image(
                        title=wp_fm_title,
                        file=ImageFile(
                            BytesIO(img_response.content), name=wp_fm_filename
                        )
                    )
                    thumbnail.save()

                    # Prep WP content for Wagtail
                    body_content = []
                    soup = BeautifulSoup(wp_post_content, 'html5lib')

                    # Alignment for images
                    align = 'pull-right'

                    for element in soup.body.children:
                        # Ignore whitespace between elements
                        if isinstance(element, str) and not element.strip():
                            continue

                        # Images
                        content_images = element.find_all('img')

                        # Is a header
                        if element.name in ['h2', 'h3', 'h4', 'h5', 'h6']:
                            body_content.append(
                                {
                                    u'type': u'{}'.format(str(element.name)),
                                    u'value': str(element.text)
                                }
                            )
                        # Has images
                        elif content_images:
                            for img in content_images:
                                wp_img_caption = img.parent.find_next_sibling(
                                    'p', class_='wp-caption-text'
                                )
                                caption = ''
                                if wp_img_caption:
                                    caption = wp_img_caption.text
                                align = toggle_img_alignment_class(align)
                                content_img_url = img['src']
                                alt = img['alt']
                                filename = content_img_url.split('/')[-1]
                                content_img_resp = get_image(content_img_url)
                                # css = img['class']
                                content_img = Image(
                                    title=alt,
                                    file=ImageFile(
                                        BytesIO(content_img_resp.content),
                                        name=filename
                                    )
                                )
                                content_img.save()
                                body_content.append(
                                    {
                                        'type': 'image',
                                        'value': {
                                            'image': content_img.id,
                                            'title': caption,
                                            'citation': '',
                                            'caption': '',
                                            'alt_text': alt,
                                            'alignment': align,
                                            'source': '',
                                            'lightbox': True
                                        }
                                    }
                                )
                        # Anything else (normal paragraph or div with text)
                        else:
                            body_content.append(
                                {
                                    u'type': u'paragraph',
                                    u'value': {
                                        u'paragraph': str(element)
                                    }
                                }
                            )

                    news_page = LibNewsPage(
                        title=wp_post_title,
                        by_text_box=wp_author_name,
                        excerpt=wp_post_excerpt,
                        thumbnail=thumbnail,
                        alt_text=wp_fm_title,
                        published_at=wp_post_published_at,
                        body=json.dumps(body_content),
                        page_maintainer=staff,
                        editor=staff,
                        content_specialist=staff,
                        unit=unit,
                    )
                    news_index_page.add_child(instance=news_page)

                    # Add Wagtail categories if any were mapped
                    if cats:
                        news_page.lib_news_categories = cats
                        news_page.save()
