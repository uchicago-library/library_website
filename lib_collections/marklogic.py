import json
import re

import requests
from django.http import Http404
from library_website.settings.base import MARKLOGIC_LDR_URL, SPARQL_ROOT
from library_website.settings.local import (
    MARKLOGIC_LDR_PASSWORD, MARKLOGIC_LDR_USER
)
from requests.auth import HTTPBasicAuth


def sp_query(manifid: str) -> str:
    """
    Construct SparQL query from collection object NOID.

    Args:
        NOID string

    Returns:
        SparQL query in the form of a string
    """
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
              }}'''.format(manifid, SPARQL_ROOT)


def get_raw_record(manifid: str) -> dict:
    """
    Query Mark Logic for metadata fields to be displayed in collection object
    page.  Dictionary comes back in not-particularly-usable form that's similar
    to how the RDF graph is internally represented.

    Args:
        NOID string

    Returns:
        Dictionary representation of the result of the SparQL query

    """
    try:
        r = requests.get(
            auth=HTTPBasicAuth(
                MARKLOGIC_LDR_USER,
                MARKLOGIC_LDR_PASSWORD,
            ),
            headers={'Content-type': 'text/turtle'},
            params={'query': sp_query(manifid)},
            url=MARKLOGIC_LDR_URL + '/sparql',
        )
        j = json.loads(r.content.decode('utf-8'))
        return j
    except ConnectionError:
        return ''


def align_field_names(dct: dict, wagtail_field_names: list) -> dict:
    """
    Arranges metadata fields for object page so that they correspond to the
    order in which those fields appear in the Wagtail admin interface.

    Args:
        Dictionary representing result of Mark Logic query, list of field
        names (strings) stored in Wagtail database for a given collection

    Returns:
        Dictionary representing metadata for display in object page

    """
    filtered_names = [
        item for item in wagtail_field_names if item in dct.keys()
    ]
    updated_dict = {key: dct[key] for key in filtered_names}
    return updated_dict


def triples_to_dict(dct: dict, wagtail_field_names: list):
    """
    Capitalizes all metadata field names and sorts them using align_field_names
    if the Wagtail database has information about which fields to display; if
    not, displays all of them in alphabetical order.

    Args:
        Dictionary represengint result of Mark Logic query, list of field
        names (strings) stored in Wagtail database for a given collection

    Returns:
        Reformatted dictionary representing metadata
    """
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


def get_record_no_parsing(manifid: str, wagtail_field_names: list) -> dict:
    """
    Queries Mark Logic for collection object metadata fields, leaves the values
    of those metadata fields alone, in their raw form.

    Args:
        NOID string, list of field names

    Returns:
        Dictionary representing metadata
    """
    raw_record = get_raw_record(manifid)
    return triples_to_dict(raw_record, wagtail_field_names)


def remove_trailing_comma(string: str) -> str:
    """
    Remove leading/trailing whitespace and trailing commas from a string.

    Args:
        Metadata string

    Returns:
        Cleaned up metadata string
    """
    stripped = string.strip()
    rev = stripped[::-1]
    if len(rev) > 0 and rev[0] == ',':
        return rev[1:][::-1]
    else:
        return rev[::-1]


def brackets_parse(value: str) -> dict:
    """
    Parses the library cataloguers' notation for stating whether an author/date
    attribution is externally derived.  Result is a representation of that
    information in dictionary form.

    Args:
        Metadata string

    Returns:
        Dictionary indicating whether author/date attributions are
        externally derived
    """

    def question_mark(qm):
        if qm is None:
            return False
        else:
            return qm == '?'

    prepped = remove_trailing_comma(value)
    extract_from_brackets = re.compile(r'^\[([\w\s\d,.]*)(\\?)?\]')
    contents = re.match(extract_from_brackets, prepped)

    if contents is not None:
        return {
            'contents': contents[1],
            'externally_derived': True,
            'uncertain': question_mark(contents[2])
        }
    else:
        return {
            'contents': prepped,
            'externally_derived': False,
            'uncertain': False
        }


def get_record_parsed(manifid: str, wagtail_field_names: list) -> dict:
    """
    Performs SparQL query, arranges result to mirror metadata fields from
    Wagtail database, and parses all of the metadata fields.

    Args:
        NOID string, list of metadata field names

    Returns:
        Dictionary of metadata fields, with parse results in values

    """
    dct = get_record_no_parsing(manifid, wagtail_field_names)
    return {k: brackets_parse(v) for k, v in dct.items()}


def render_field(parsed_field: dict) -> str:
    """
    Render a metadata field parse object as a string, for display in the object
    page.

    Args:
        Field parse object

    Returns:
        String representing how that field will be displayed in the template
    """

    def question_mark(yes_qm):
        if yes_qm:
            return '?'
        else:
            return ''

    try:
        if parsed_field['externally_derived']:
            return "[%s%s]" % (
                parsed_field['contents'],
                question_mark(parsed_field['uncertain']),
            )
        else:
            return parsed_field['contents']
    except KeyError:
        return parsed_field


def get_record_for_display(manifid: str, wagtail_field_names: list) -> dict:
    """
    Main function for getting metadata fields back from Mark Logic, based on a
    collection object's NOID.

    Args:
        NOID string, list of metadata field names

    Returns:
        Dictionary representing metadata to be displayed on collection
        object page.
    """
    dct = get_record_parsed(manifid, wagtail_field_names)
    return {k: render_field(v) for k, v in dct.items()}
