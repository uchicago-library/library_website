import json
from urllib.parse import urlparse

from django.http import Http404
import requests
import re
from requests.auth import HTTPBasicAuth
# from .utils import DisplayBrowse

from library_website.settings.local import (MARKLOGIC_LDR_PASSWORD,
                                            MARKLOGIC_LDR_USER)


def sp_query(manifid):
    MARKLOGIC_ROOT = "https://repository.lib.uchicago.edu/digital_collections"
    return '''SELECT ?coverage ?creator ?date ?description ?format ?identifier ?publisher ?rights ?subject ?title ?type ?ClassificationLcc ?Local
              FROM <{1}>
              WHERE {{
                  <ark:61001/{0}> <http://purl.org/dc/elements/1.1/identifier> ?identifier .
                  OPTIONAL {{ <ark:61001/{0}> <http://purl.org/dc/elements/1.1/creator> ?coverage .  }}
                  OPTIONAL {{ <ark:61001/{0}> <http://purl.org/dc/elements/1.1/creator> ?creator .  }}
                  OPTIONAL {{ <ark:61001/{0}> <http://purl.org/dc/elements/1.1/date> ?date . }}
                  OPTIONAL {{ <ark:61001/{0}> <http://purl.org/dc/elements/1.1/description> ?description . }}
                  OPTIONAL {{ <ark:61001/{0}> <http://purl.org/dc/elements/1.1/format> ?format . }}
                  OPTIONAL {{ <ark:61001/{0}> <http://purl.org/dc/elements/1.1/publisher> ?publisher . }}
                  OPTIONAL {{ <ark:61001/{0}> <http://purl.org/dc/elements/1.1/rights> ?rights . }}
                  OPTIONAL {{ <ark:61001/{0}> <http://purl.org/dc/elements/1.1/subject> ?subject .  }}
                  OPTIONAL {{ <ark:61001/{0}> <http://purl.org/dc/elements/1.1/title> ?title . }}
                  OPTIONAL {{ <ark:61001/{0}> <http://purl.org/dc/elements/1.1/type> ?type . }}
                  OPTIONAL {{ <ark:61001/{0}> <http://id.loc.gov/ontologies/bibframe/ClassificationLcc> ?ClassificationLcc . }}
                  OPTIONAL {{ <ark:61001/{0}> <http://id.loc.gov/ontologies/bibframe/Local> ?Local . }}
              }}'''.format(manifid, MARKLOGIC_ROOT)


def get_raw_record(manifid):
    r = requests.get(
        auth=HTTPBasicAuth(
            MARKLOGIC_LDR_USER,
            MARKLOGIC_LDR_PASSWORD,
        ),
        headers={'Content-type': 'text/turtle'},
        params={'query': sp_query(manifid)},
        url='http://marklogic.lib.uchicago.edu:8008/v1/graphs/sparql'
    )
    j = json.loads(r.content.decode('utf-8'))
    return j


# def collections_query(manifest_url):
#     raise NotImplementedError


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
    except IndexError:
        raise Http404


def get_record_no_parsing(manifid, slug, wagtail_field_names):
    # manifest_url = mk_manifest_url(manifid, slug)
    raw_record = get_raw_record(manifid)
    # return raw_record
    return triples_to_dict(raw_record, wagtail_field_names)


def brackets_parse(value):
    def question_mark(qm):
        if qm is None:
            return False
        else:
            return qm == '?'

    prepped = remove_trailing_comma(value)
    extract_from_brackets = re.compile("^\[([\w\s\d,.]*)(\\?)?\]")
    contents = re.match(extract_from_brackets, prepped)

    if contents is not None:
        return {'contents': contents[1],
                'externally_derived': True,
                'uncertain': question_mark(contents[2])}
    else:
        return {'contents': prepped,
                'externally_derived': False,
                'uncertain': False}


def remove_trailing_comma(string):
    stripped = string.strip()
    rev = stripped[::-1]
    if len(rev) > 0 and rev[0] == ',':
        return rev[1:][::-1]
    else:
        return rev[::-1]


def get_record_parsed(manifid, slug, wagtail_field_names):
    dct = get_record_no_parsing(manifid, slug, wagtail_field_names)
    return {k: brackets_parse(v) for k, v in dct.items()}


def render_field(parsed_field):
    def question_mark(yes_qm):
        if yes_qm:
            return '?'
        else:
            return ''
    try:
        if parsed_field['externally_derived']:
            return "[%s%s]" % (parsed_field['contents'],
                               question_mark(parsed_field['uncertain']),
                               )
        else:
            return parsed_field['contents']
    except KeyError:
        return parsed_field


def get_record_for_display(manifid, slug, wagtail_field_names):
    dct = get_record_parsed(manifid, slug, wagtail_field_names)
    return {k: render_field(v) for k, v in dct.items()}