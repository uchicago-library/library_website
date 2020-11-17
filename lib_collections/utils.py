"""
iiifcollectionbrowse
"""

from django.utils.text import slugify
from django.http.response import Http404
from functools import reduce
from datetime import date

import requests
import re


from .exceptions import (IncompatibleRecordError, InvalidCollectionRecordError,
                         NoCollectionFoundError, NoCollectionParameterError)

LANGUAGE_ABBREVS = {'en': 'English'}

# toggle this comment to go between dev and production
IIIF_PREFIX = "https://iiif-collection.lib.uchicago.edu"
# IIIF_PREFIX = "https://iiif-collection-dev.lib.uchicago.edu"

WAGTAIL_PREFIX = "/collex/collections"


class CBrowseURL():
    """
    Namespace class containing utility functions for creating cluster
    browse URLs for both Wagtail and IIIF
    """
    def mk_cbrowse_url(prefix, slug, browse_type, browse_name, extension):
        return "%s/%s/cluster-browse/%s/%s%s" % (
            prefix,
            slug,
            browse_type,
            browse_name,
            extension
        )

    def mk_cbrowse_url_iiif(slug, browse_name, browse_type):
        return CBrowseURL.mk_cbrowse_url(
            IIIF_PREFIX,
            slug,
            browse_type,
            browse_name,
            ".json"
        )

    def mk_cbrowse_url_wagtail(slug, browse_type, browse_name, full=False):
        url = CBrowseURL.mk_cbrowse_url(
            WAGTAIL_PREFIX,
            slug,
            browse_type,
            browse_name,
            ""
        )
        if full:
            return "https://www.lib.uchicago.edu" + url
        else:
            return url

    def mk_cbrowse_type_url(prefix, slug, browse_type, extension):
        return "%s/%s/cluster-browse/%s%s" % (
            prefix,
            slug,
            browse_type,
            extension
        )

    def mk_cbrowse_type_url_iiif(slug, browse_type):
        return CBrowseURL.mk_cbrowse_type_url(
            IIIF_PREFIX,
            slug,
            browse_type,
            ".json"
        )

    def mk_cbrowse_type_url_wagtail(slug, browse_type, full=False):
        url = CBrowseURL.mk_cbrowse_type_url(
            WAGTAIL_PREFIX,
            slug,
            browse_type,
            ""
        )
        if full:
            return "https://www.lib.uchicago.edu" + url
        else:
            return url


class LBrowseURL():
    """
    Namespace class containing utility functions for creating list
    browse URLs for both Wagtail and IIIF

    """
    def mk_lbrowse_url(prefix, slug, browse_name, extension):
        return "%s/%s/list-browse/%s%s" % (
            prefix,
            slug,
            browse_name,
            extension
        )

    def mk_lbrowse_url_iiif(slug, browse_name):
        return LBrowseURL.mk_lbrowse_url(
            IIIF_PREFIX,
            slug,
            browse_name,
            ".json"
        )

    def mk_lbrowse_url_wagtail(slug, browse_name):
        return LBrowseURL.mk_lbrowse_url(
            WAGTAIL_PREFIX,
            slug,
            browse_name,
            ""
        )


class DisplayBrowse():
    """
    Namespace class containing code for generating digital collection
    object listings, intermediate cluster browses, and object page
    links Wagtail

    """
    def unslugify_browse(slug):
        slug_list = slug.split('-')
        spaces = ' '.join([x.capitalize() for x in slug_list])
        return spaces

    def get_iiif_labels_language(url, lang):
        r = requests.get(url)
        if r.status_code == 404:
            raise Http404
        else:
            j = r.json()
            d = j['items']
            return [x['label'][lang][0] for x in d]

    def get_iiif_labels(url, browse_type, slug):

        def lists_to_dict(lst1, lst2):
            return dict(zip(lst1, lst2))

        labels = DisplayBrowse.get_iiif_labels_language(url, 'en')
        return lists_to_dict(labels,
                             [CBrowseURL.mk_cbrowse_url_wagtail(
                                 slug,
                                 browse_type,
                                 slugify(label))
                                 for label in labels])

    def mk_wagtail_object_url(collection_slug, manifid):
        return ("/collex/collections/%s/object/%s"
                % (collection_slug, manifid)
                )

    def mk_manifest_url(manifid, slug):
        return "%s/%s/object/%s.json" % (IIIF_PREFIX, slug, manifid)

    def mk_viewer_url(manifid, slug):
        # toggle this comment with the other to switch from dev to production
        prefix = "https://liblet.lib.uchicago.edu/viewer?manifest="
        # prefix = "https://www.lib.uchicago.edu/viewer?manifest="
        return prefix + DisplayBrowse.mk_manifest_url(manifid, slug)

    def create_field(name, dct):
        if name in dct.keys():
            return dct[name]
        else:
            return []

    def iiif_field_update(dct, field, val):
        if field in dct.keys():
            new_value = dct[field] + [val]
            dct.update({field: new_value})
        else:
            dct[field] = [val]

    def pull_metadata_labels(j):
        output = {}
        for x in j['metadata']:
            DisplayBrowse.iiif_field_update(
                output,
                x['label']['en'][0].lower(),
                x['value']['en'][0],
            )
        return output

    def prepare_browse_json(j, joiner):
        manifid = DisplayBrowse.extract_manifid_thumbnail(
            j['thumbnail'][0]['id'])

        metadata = DisplayBrowse.pull_metadata_labels(j)
        create_field = DisplayBrowse.create_field

        title = create_field('title', metadata)
        publisher = create_field('publisher', metadata)
        creator = create_field('creator', metadata)
        date = create_field('date', metadata)
        language = create_field('language', metadata)

        output = {'title': joiner(title),
                  'creator': joiner(creator),
                  'date': joiner(date),
                  'publisher': joiner(publisher),
                  'language': joiner([LANGUAGE_ABBREVS[x] for x in language]),
                  'image_link': j['thumbnail'][0]['id'],
                  'manifest': j['id'],
                  'manifid': manifid,
                  'wagtail_link': DisplayBrowse.mk_wagtail_object_url(
                      'social-scientists-map-chicago', manifid),
                  }
        return output

    def extract_manifid_thumbnail(url):
        rexp = re.search('.*\/ark\%3A61001\%2F([\d|\w]+)/', url)
        try:
            return rexp[1]
        except TypeError:
            return ''
