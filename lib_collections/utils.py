"""
iiifcollectionbrowse
"""
from threading import Thread
from urllib.parse import unquote
from django.utils.text import slugify
from django.http.response import Http404
from functools import reduce
from datetime import date

import requests
import re


# from pyiiif.pres_api.utils import get_thumbnail

from .exceptions import (IncompatibleRecordError, InvalidCollectionRecordError,
                         NoCollectionFoundError, NoCollectionParameterError)

config = {
    "VIEWER_URL": "https://iiif-viewer.lib.uchicago.edu/uv/uv.html#",
    "REQUESTS_TIMEOUT": 1,
    "NO_THUMB_IMG_URL": '',
    "CONTRAST_COLOR": "#800000",
    "THUMBNAIL_BACKDROP": "#D6D6CE"
}

VIEWER_URL = config['VIEWER_URL']
REQUESTS_TIMEOUT = float(config['REQUESTS_TIMEOUT'])
NO_THUMB_IMG_URL = config['NO_THUMB_IMG_URL']
THUMBS_PER_PAGE = 10
COLORS = {
    "contrast_color": config['CONTRAST_COLOR'],
    "thumbnail_backdrop": config['THUMBNAIL_BACKDROP']
}


def threaded_thumbnails(identifier, result, index):
    """
    Wraps get_thumbnail() for multi-threaded solutions

    The array should be "initialized" to the correct size,
    and each thread should deposit it's thumbnail into the
    appropriate index.

    Args:
        identifier: string

        result: list

        index: int

    Returns:
        None
    """
    result[index] = get_thumbnail(identifier)


def build_collection_url(ident, page=1):
    """
    Builds the URL to render a collection record
    in this interface.

    Args:
        ident: string, the record identifier (url)

        page: string, the page number to render, if using
        the thumbnail view.

    Returns:
        string, the url which will render the collection record at
        the provided url.
    """
    return "?record={}&page={}".format(ident, str(page))


def record_compatible(rec):
    """
    Determines if a collection record is compatible with the interface.

    Returns:
        bool, True if record is compatible, otherwise False.
    """
    # TODO
    # NOTE: This is primarily meant to be a method to provide
    # for graceful failure. What we do in this case is up in the air.
    # Link the user to the JSON?
    # Display a sad-face emoji?
    # Let the provider register a callback to run?
    return True


def get_clist_html(members, manifests, collections, viewer_url):
    """
    Get the display html for the collections list navigation.

    Args:
        members: list

        manifests: list

        collections: list

        viewer_url: string

    Returns:
        string, html
    """
    retval = ''
    combined = members + manifests + collections
    if len(combined) > 0:
        retval += '<ul>'
        for m in combined:
            if m['@type'] == 'sc:Collection':
                retval += '<li><a href="%s">%s</a></li>' % (
                    m['t_url'], m['label']
                )
            else:
                retval += '<li><a href="%s?manifest=%s">%s</a></li>' % (
                    viewer_url, m['@id'], m['label']
                )
        retval += '</ul>'
    return retval


def get_cthumb_html(members, manifests, collections, viewer_url):
    """
    Get the display html for collection thumbnails.

    Args:
        members: list

        manifests: list

        collections: list

        viewer_url: string

    Returns:
        string, html
    """
    retval = ''
    combined = members + manifests + collections
    if len(combined) > 0:
        retval += '<section class="thumbnails">'
        retval += '<figure>'
        for m in combined:
            if m['@type'] == 'sc:Collection':
                retval += '<a href="%s">' % (m['t_url'])
            else:
                retval += '<a href="%s?manifest=%s">' % (viewer_url, m['@id'])

            if 'thumb_url' in m:
                retval += '<img src="%s">' % (m['thumb_url'])
            retval += '<figcaption><h3><a href="%s?manifest=%s">%s</a></h3></figcaption>' % (
                viewer_url, m['@id'], m['label']
            )
            retval += '</a>'
        retval += '</figure>'
        retval += '</section>'
    return retval


def build_pagination_links(total, thumbs_per_page, current_page, rj):
    """
    Generate a navigation menu of all pages.

    Args:
        total: int, number of thumbnails being paginated.

        thumbs_per_page: number of thumbnails to display
        per page.

        current_page: int, the current page being viewed.

        rj: json response with thumbnail data.

    Returns:
        Generator, html menu of links.
    """
    page = 1
    pagination_links = ''
    while page <= (total / thumbs_per_page):
        active = page == current_page
        active_css = ''
        if active:
            active_css = 'disabled aria-disabled="true"'
        pagination_links += '<a href="%s" %s>[%s]</a> ' % (
            build_collection_url(rj['@id'], page=page), active_css, str(page)
        )
        page += 1
    yield pagination_links


IIIF_PATHS = {
    "social-scientists-map-chicago": ["maps", "chisoc"],
    # TODO: eliminiate this silly test example
    "century-progress-international-exposition-publications": ["maps", "chisoc"],
}

IIIF_PREFIX = "https://iiif-collection.lib.uchicago.edu"

MANIFEST_PREFIX = "https://iiif-manifest.lib.uchicago.edu"


def dot(f, g):
    return lambda x: f(g(x))


def compose(*args):
    return reduce(dot, args)


def lists_to_dict(lst1, lst2):
    return dict(zip(lst1, lst2))


def slug_to_iiif_path(slug):
    try:
        return '/'.join(IIIF_PATHS[slug])
    except KeyError:
        return ''


def mk_subjects_url(slug):
    return "%s/%s/%s-subjects.json" % (
        IIIF_PREFIX, slug_to_iiif_path(slug), IIIF_PATHS[slug][-1]
    )


def mk_subject_iiif_url(subj, slug):
    return "%s/%s/%s-subjects-%s.json" % (
        IIIF_PREFIX,
        slug_to_iiif_path(slug),
        IIIF_PATHS[slug][-1],
        slugify(subj),
    )


def unslugify_browse(slug):
    slug_list = slug.split('-')
    spaces = ' '.join(slug_list)
    return spaces[0].upper() + spaces[1:]


def get_iiif_labels_language(url, lang):
    r = requests.get(url)
    if r.status_code == 404:
        raise Http404
    else:
        j = r.json()
        d = j['items']
        # return d
        return [x['label'][lang][0] for x in d]


def get_iiif_listing(url):
    r = requests.get(url)
    if r.status_code == 404:
        raise Http404
    else:
        j = r.json()
        d = j['items']
        return d


def get_iiif_labels(url, slug):
    labels = get_iiif_labels_language(url, 'en')
    return lists_to_dict(
        labels, [slugify(x) for x in labels]
    )


def mk_manifest_url(manifid, slug):
    return "%s/%s/%s/%s.json" % (
        MANIFEST_PREFIX, slug_to_iiif_path(slug), manifid, manifid
    )


def extract_manifid(url):
    rexp = re.search(r".*\/(.*)\.json", url)
    if rexp[1] is not None:
        return rexp[1]
    else:
        return ''


# TODO: replace the dummy data: creator, date, publisher, language,
# 'social-scientists-maps-chicago'


def prepare_browse_json(j):
    manifid = extract_manifid(j['id'])
    output = {'title': j['label']['en'][0],
              'creator': '[ IIIF Creator info coming soon! ]',
              'date': '[ IIIF Date info coming soon! ]',
              'publisher': '[ IIIF Publisher info coming soon! ]',
              'language': '[ IIIF Language coming soon! ]',
              'image_link': j['thumbnail'][0]['id'],
              'manifest': j['id'],
              'manifid': manifid,
              'wagtail_link': mk_wagtail_object_url(
                  'social-scientists-map-chicago', manifid),
              }
    return output


def mk_wagtail_object_url(collection_slug, manifid):
    return ("/collex/collections/%s/object/%s"
            % (collection_slug, manifid)
            )


def mk_viewer_url(manifid, slug):
    prefix = "https://iiif-viewer.lib.uchicago.edu/uv/./uv.html#?manifest="
    return prefix + mk_manifest_url(manifid, slug)


def collection(request, is_viewer, manifest=''):
    """
    Get iiif manifest and collection data to append to a Wagtail
    context for rendering in templates.

    Args:
        request: object

        manifest: string, url

        is_viewer: boolean, is it a view of the universal viewer

    Returns:
        dictionary
    """

    viewer_url = request.path + 'viewer/'

    # Try to pull the collection record, else a default, else error
    if not request.GET.get('record'):
        if manifest:
            c_url = manifest
        else:
            raise NoCollectionParameterError()
    else:
        c_url = request.GET.get('record')

    try:
        resp = requests.get(c_url, timeout=REQUESTS_TIMEOUT)
        resp.raise_for_status()
        rj = resp.json()
    except Exception:
        raise NoCollectionFoundError(
            "Could not find a collection JSON record at {}".format(c_url)
        )
    for x in ('@id', 'label'):
        if not rj.get(x):
            raise InvalidCollectionRecordError(
                "Could not find '@id' and 'label' keys in the JSON at {}".
                format(c_url)
            )

    # Be sure the interface can render this record,
    # as some valid records may be unrenderable due
    # to technical constraints.
    if not record_compatible(rj):
        raise IncompatibleRecordError()

    # Parse the record
    members = []
    collections = []
    manifests = []
    if rj.get("members"):
        members = rj['members']
    if rj.get('collections'):
        collections = rj['collections']
    if rj.get('manifests'):
        manifests = rj['manifests']

    # Build template urls
    for x in collections:
        x['t_url'] = build_collection_url(x['@id'])
    for x in members:
        if x['@type'] == "sc:Collection":
            x['t_url'] = build_collection_url(x['@id'])

    # Get if the current request is paginated or not
    page = request.GET.get("page", 1)
    try:
        page = int(page)
    except Exception:
        page = 1

    # Thumbnail view - paginated
    if rj.get('viewingHint') == "individuals" and page > 0:
        # 30 results per page max, to not block too long on
        # dynamically generating thumbnails even in bad cases
        total = max(len(members), len(collections), len(manifests))
        start = (page - 1) * THUMBS_PER_PAGE
        end = page * THUMBS_PER_PAGE

        # Generate sublists of just the stuff for this page
        members = members[start:end]
        collections = collections[start:end]
        manifests = manifests[start:end]

        # Assemble page links and stuff
        list_view = build_collection_url(rj['@id'], page=-1)
        if end > total:
            next_page = None
        else:
            next_page = build_collection_url(rj['@id'], page=page + 1)
        prev_page = None
        if page > 1:
            prev_page = build_collection_url(rj['@id'], page=page - 1)

        # Handle thumbnail finding for viewingHint == individuals
        # https://stackoverflow.com/questions/6893968/
        # how-to-get-the-return-value-from-a-thread-in-python
        # Note: This makes the order in which the lists are
        # concatonated important - otherwise thumbnails won't match.
        results = [None] * len(members + collections + manifests)
        for i, x in enumerate(members + collections + manifests):
            x['thumb_thread'] = Thread(
                target=threaded_thumbnails, args=(x['@id'], results, i)
            )
            x['thumb_thread'].start()
        for i, x in enumerate(members + collections + manifests):
            x['thumb_thread'].join(timeout=10)
            if results[i] is not None:
                # This call to unquote is a hack to get the thumbnails
                # to work against a Loris server until we figure out
                # why our apache setup isn't passing escaped URLs through
                # to the server
                x['thumb_url'] = unquote(results[i])
            else:
                x['thumb_url'] = NO_THUMB_IMG_URL
        return {
            'template':
            'lib_collections/collection_thumbnails.html',
            'pagination_menu':
            build_pagination_links(total, THUMBS_PER_PAGE, page, rj),
            'is_browse':
            True,
            'viewer_url':
            viewer_url,
            'cname':
            rj['label'],
            'cdesc':
            rj.get('description'),
            'list_view':
            list_view,
            'next_page':
            next_page,
            'prev_page':
            prev_page,
            'members':
            members,
            'collections':
            collections,
            'manifests':
            manifests,
            'collection_list_html':
            get_clist_html(members, manifests, collections, viewer_url),
            'collection_thumbs_html':
            get_cthumb_html(members, manifests, collections, viewer_url),
            'colors':
            COLORS
        }
    # Embedded universal viewer
    elif is_viewer:
        return {
            'template': 'lib_collections/collection_item_viewer.html',
            'viewer_url': viewer_url,
            'image_manifest': request.GET.get('manifest'),
        }
    # List view - no pagination
    else:
        thumbnail_view = None
        if rj.get('viewingHint') == 'individuals':
            thumbnail_view = build_collection_url(rj['@id'], page=1)
        return {
            'template':
            'lib_collections/collection_list.html',
            'is_browse':
            True,
            'viewer_url':
            viewer_url,
            'cname':
            rj['label'],
            'cdesc':
            rj.get('description'),
            'members':
            members,
            'collections':
            collections,
            'manifests':
            manifests,
            'collection_list_html':
            get_clist_html(members, manifests, collections, viewer_url),
            'collection_thumbs_html':
            get_cthumb_html(members, manifests, collections, viewer_url),
            'colors':
            COLORS,
            'thumbnail_view':
            thumbnail_view
        }
