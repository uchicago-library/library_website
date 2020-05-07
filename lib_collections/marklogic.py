import json
from urllib.parse import urlparse

import requests
from requests.auth import HTTPBasicAuth

from library_website.settings.local import (MARKLOGIC_LDR_PASSWORD,
                                            MARKLOGIC_LDR_USER)


def manifest_url_to_cho(u):
    # convert a manifest url to a cho:
    # /digital_collections/IIIF_Files/maps/chisoc/G4104-C6-1933-U5-a
    path_parts = urlparse(u).path.replace('.json', '').split('/')
    path_parts.pop()
    path = '/'.join(path_parts)
    return '/digital_collections/IIIF_Files{}'.format(path)


def sp_query(s):
    return '''SELECT ?coverage ?creator ?date ?description ?format ?identifier ?publisher ?rights ?subject ?title ?type
              FROM <http://lib.uchicago.edu/digital_collections/maps/chisoc>
              WHERE {{
                  <{0}> <http://purl.org/dc/elements/1.1/identifier> ?identifier .
                  OPTIONAL {{ <{0}> <http://purl.org/dc/elements/1.1/creator> ?coverage .  }}
                  OPTIONAL {{ <{0}> <http://purl.org/dc/elements/1.1/creator> ?creator .  }}
                  OPTIONAL {{ <{0}> <http://purl.org/dc/elements/1.1/date> ?date . }}
                  OPTIONAL {{ <{0}> <http://purl.org/dc/elements/1.1/description> ?description . }}
                  OPTIONAL {{ <{0}> <http://purl.org/dc/elements/1.1/format> ?format . }}
                  OPTIONAL {{ <{0}> <http://purl.org/dc/elements/1.1/publisher> ?publisher . }}
                  OPTIONAL {{ <{0}> <http://purl.org/dc/elements/1.1/rights> ?rights . }}
                  OPTIONAL {{ <{0}> <http://purl.org/dc/elements/1.1/subject> ?subject .  }}
                  OPTIONAL {{ <{0}> <http://purl.org/dc/elements/1.1/title> ?title . }}
                  OPTIONAL {{ <{0}> <http://purl.org/dc/elements/1.1/type> ?type . }}
              }}'''.format(manifest_url_to_cho(s))


def collections_query(manifest_url):
    raise NotImplementedError


test_url = 'https://iiif-manifest.lib.uchicago.edu/maps/chisoc/G4104-C6-2N3E51-1908-S2/G4104-C6-2N3E51-1908-S2.json'


def align_field_names(dct, wagtail_field_names):
    filtered_names = [item
                      for item in wagtail_field_names
                      if item in dct.keys()]
    updated_dict = {key: dct[key] for key in filtered_names}
    return updated_dict


def triples_to_dict(dct, wagtail_field_names):
    try:
        results = dct['results']['bindings'][0]
        field_dict = {
            key.capitalize(): results[key]['value'] for key in results.keys()
        }
        if wagtail_field_names:
            return align_field_names(field_dict, wagtail_field_names)
        else:
            return field_dict
    except KeyError:
        raise Exception("Mark Logic result not formatted as expected")


def get_raw_record(manifest_url, wagtail_field_names):
    r = requests.get(
        auth=HTTPBasicAuth(
            MARKLOGIC_LDR_USER,
            MARKLOGIC_LDR_PASSWORD,
        ),
        headers={'Content-type': 'text/turtle'},
        params={'query': sp_query(manifest_url)},
        url='http://marklogic.lib.uchicago.edu:8008/v1/graphs/sparql'
    )
    j = json.loads(r.content.decode('utf-8'))
    return j


def get_record(manifest_url, wagtail_field_names):
    raw_record = get_raw_record(manifest_url, wagtail_field_names)
    return triples_to_dict(raw_record, wagtail_field_names)
