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


def manifest_url_to_dc_xml(u):
    # /digital_collections/IIIF_Files/maps/chisoc/G4104-C6-2N3E51-1908-S2/G4104-C6-2N3E51-1908-S2.dc.xml
    return '{}.dc.xml'.format(manifest_url_to_cho(u))


def manifest_url_to_agg(u):
    # /aggregation/digital_collections/IIIF_Files/maps/chisoc/G4104-C6-2N3E51-1908-S2/G4104-C6-2N3E51-1908-S2.dc.xml
    return '/aggregation{}'.format(manifest_url_to_cho(u))


def manifest_url_to_rem(u):
    # /rem/digital_collections/IIIF_Files/maps/chisoc/G4104-C6-2N3E51-1908-S2/G4104-C6-2N3E51-1908-S2
    return '/rem{}'.format(manifest_url_to_cho(u))


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


# def get_record(manifest_url):
#     response = requests.get(
#         auth=HTTPBasicAuth(MARKLOGIC_LDR_USER, MARKLOGIC_LDR_PASSWORD),
#         headers={'Content-type': 'text/turtle'},
#         params={'query': sp_query(manifest_url)},
#         url='http://marklogic.lib.uchicago.edu:8008/v1/graphs/sparql'
#     )
#     json_value = json.loads(response.content.decode('utf-8'))
#     return json_value


def triples_to_dict(dct):
    try:
        results = dct['results']['bindings'][0]
        # return results
        return { key: results[key]['value'] for key in results.keys() }
    except KeyError:
        raise Exception("Mark Logic result not formatted as expected")

def get_record(manifest_url):
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
    return triples_to_dict(j)
