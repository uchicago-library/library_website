import json
import os
import re

import requests
import simplejson

try:
    from library_website.settings import (
        MARKLOGIC_LDR_PASSWORD,
        MARKLOGIC_LDR_URL,
        MARKLOGIC_LDR_USER,
        SPARQL_ROOT,
    )
except ImportError:
    MARKLOGIC_LDR_PASSWORD = os.environ["MARKLOGIC_LDR_PASSWORD"]
    MARKLOGIC_LDR_USER = os.environ["MARKLOGIC_LDR_USER"]
    MARKLOGIC_LDR_URL = os.environ["MARKLOGIC_LDR_URL"]
    SPARQL_ROOT = os.environ["SPARQL_ROOT"]

from requests.auth import HTTPBasicAuth

from lib_collections.utils import GeneralPurpose


def sp_query(manifid: str) -> str:
    """
    Construct SparQL query from collection object NOID.

    Args:
        manifid: string, ARK NOID

    Returns:
        SparQL query in the form of a string
    """
    return """SELECT ?coverage ?creator ?date ?description ?format ?identifier ?publisher ?rights ?subject ?title ?type ?spatial ?ClassificationLcc ?Local
              FROM <{1}>
              WHERE {{
                  <ark:61001/{0}> <http://purl.org/dc/elements/1.1/identifier> ?identifier .
                  OPTIONAL {{ <ark:61001/{0}> <http://purl.org/dc/elements/1.1/creator> ?creator . }}
                  OPTIONAL {{ <ark:61001/{0}> <http://purl.org/dc/elements/1.1/date> ?date . }}
                  OPTIONAL {{ <ark:61001/{0}> <http://purl.org/dc/elements/1.1/description> ?description . }}
                  OPTIONAL {{ <ark:61001/{0}> <http://purl.org/dc/elements/1.1/format> ?format . }}
                  OPTIONAL {{ <ark:61001/{0}> <http://purl.org/dc/elements/1.1/publisher> ?publisher . }}
                  OPTIONAL {{ <ark:61001/{0}> <http://purl.org/dc/elements/1.1/rights> ?rights . }}
                  OPTIONAL {{ <ark:61001/{0}> <http://purl.org/dc/elements/1.1/subject> ?subject .  }}
                  OPTIONAL {{ <ark:61001/{0}> <http://purl.org/dc/elements/1.1/title> ?title . }}
                  OPTIONAL {{ <ark:61001/{0}> <http://purl.org/dc/elements/1.1/type> ?type . }}
                  OPTIONAL {{ <ark:61001/{0}> <http://purl.org/dc/terms/spatial> ?spatial . }}
                  OPTIONAL {{ <ark:61001/{0}> <http://id.loc.gov/ontologies/bibframe/ClassificationLcc> ?ClassificationLcc . }}
                  OPTIONAL {{ <ark:61001/{0}> <http://id.loc.gov/ontologies/bibframe/Local> ?Local . }}
              }}""".format(
        manifid, SPARQL_ROOT
    )


def get_raw_record(
    manifid: str, modify=GeneralPurpose.noop, func=GeneralPurpose.identity
) -> dict:
    """
    Query Mark Logic for metadata fields to be displayed in collection object
    page.  Dictionary comes back in not-particularly-usable form that's similar
    to how the RDF graph is internally represented.  Optional func parameter
    only there to help with unit testing.

    Args:
        manifid: string, ARK NOID

    Returns:
        Dictionary representation of the result of the SparQL query

    """
    try:
        r = requests.get(
            auth=HTTPBasicAuth(
                MARKLOGIC_LDR_USER,
                MARKLOGIC_LDR_PASSWORD,
            ),
            headers={"Content-type": "text/turtle"},
            params={"query": sp_query(manifid)},
            url=MARKLOGIC_LDR_URL + "/sparql",
        )
        modify(r)
        j = json.loads(r.content.decode("utf-8"))
        return func(j)
    except requests.exceptions.RequestException:
        return ""


def align_field_names(dct: dict, wagtail_field_names: list) -> dict:
    """
    Arranges metadata fields for object page so that they correspond to the
    order in which those fields appear in the Wagtail admin interface.

    Args:
        dct: Dictionary representing result of Mark Logic query,

        wagtail_field_names: list of field names (strings) stored in
        Wagtail database for a given collection

    Returns:
        Dictionary representing metadata for display in object page

    """
    filtered_names = [item for item in wagtail_field_names if item in dct.keys()]
    updated_dict = {key: dct[key] for key in filtered_names}
    return updated_dict


def triples_to_dict(dct: dict, wagtail_field_names: list):
    """
    Capitalizes all metadata field names and sorts them using align_field_names
    if the Wagtail database has information about which fields to display; if
    not, displays all of them in alphabetical order.

    Args:
        dct: Dictionary representing result of Mark Logic query,

        wagtail_field_names: list of field names (strings) stored in
        Wagtail database for a given collection

    Returns:
        Reformatted dictionary representing metadata
    """
    try:
        results = dct["results"]["bindings"][0]
        field_dict = {key.capitalize(): results[key]["value"] for key in results.keys()}
        if wagtail_field_names:
            return align_field_names(field_dict, wagtail_field_names)
        else:
            return field_dict
    except (KeyError, IndexError):
        return ""


def get_record_no_parsing(
    manifid: str,
    wagtail_field_names: list,
    modify=GeneralPurpose.noop,
    func=GeneralPurpose.identity,
) -> dict:
    """
    Queries Mark Logic for collection object metadata fields, leaves the values
    of those metadata fields alone, in their raw form.

    Args:
        manifid: string, ARK NOID

        wagtail_field_names: list of field names (strings) stored in
        Wagtail database for a given collection

    Returns:
        Dictionary representing metadata
    """
    raw_record = get_raw_record(manifid, modify=modify, func=func)
    if raw_record:
        return triples_to_dict(raw_record, wagtail_field_names)
    else:
        return ""


def remove_trailing_comma(string: str) -> str:
    """
    Remove leading/trailing whitespace and trailing commas from a string.

    Args:
        string: string containing metadata

    Returns:
        Cleaned up metadata string
    """
    stripped = string.strip()
    rev = stripped[::-1]
    if len(rev) > 0 and rev[0] == ",":
        return rev[1:][::-1]
    else:
        return rev[::-1]


def brackets_parse(value: str) -> dict:
    """
    Parses the library cataloguers' notation for stating whether an author/date
    attribution is externally derived.  Result is a representation of that
    information in dictionary form.

    Args:
        string: string containing metadata

    Returns:
        Dictionary indicating whether author/date attributions are
        externally derived
    """

    def question_mark(qm):
        if qm is None:
            return False
        else:
            return qm == "?"

    prepped = remove_trailing_comma(value)
    extract_from_brackets = re.compile(r"^\[([\w\s\d,.]*)(\\?)?\]")
    contents = re.match(extract_from_brackets, prepped)

    if contents is not None:
        return {
            "contents": contents[1],
            "externally_derived": True,
            "uncertain": question_mark(contents[2]),
        }
    else:
        return {"contents": prepped, "externally_derived": False, "uncertain": False}


def get_record_parsed(
    manifid: str,
    wagtail_field_names: list,
    modify=GeneralPurpose.noop,
    func=GeneralPurpose.identity,
) -> dict:
    """
    Performs SparQL query, arranges result to mirror metadata fields from
    Wagtail database, and parses all of the metadata fields.

    Args:
        manifid: string, ARK NOID

        wagtail_field_names: list of field names (strings) stored in
        Wagtail database for a given collection

    Returns:
        Dictionary of metadata fields, with parse results in values

    """
    dct = get_record_no_parsing(manifid, wagtail_field_names, modify=modify, func=func)
    if dct:
        return {k: brackets_parse(v) for k, v in dct.items()}
    else:
        return ""


def render_field(parsed_field: dict) -> str:
    """
    Render a metadata field parse object as a string, for display in the object
    page.

    Args:
        dict: dictionary encoding a parsetree for a metadata field

    Returns:
        String representing how that field will be displayed in the template
    """

    def question_mark(yes_qm):
        if yes_qm:
            return "?"
        else:
            return ""

    try:
        if parsed_field["externally_derived"]:
            return "[%s%s]" % (
                parsed_field["contents"],
                question_mark(parsed_field["uncertain"]),
            )
        else:
            return parsed_field["contents"]
    except KeyError:
        return parsed_field


def add_extra_fields(manifid: str, dct: dict) -> dict:
    """
    Add 'parent collection' and 'permanent url' to the end of a list
    of metadata fields.  (We do this on every object page.)

    Args:
        manifid: string, ARK NOID

    Returns:
        Nothing; mutates the input dictionary
    """
    ark_base = "https://www.lib.uchicago.edu/ark:/61001/"
    dct["Collection"] = "Social Scientists Map Chicago"
    dct["Permanent URL"] = ark_base + manifid


def get_record_for_display(
    manifid: str,
    wagtail_field_names: list,
    modify=GeneralPurpose.noop,
    func=GeneralPurpose.identity,
) -> dict:
    """
    Main function for getting metadata fields back from Mark Logic, based on a
    collection object's NOID.

    Args:
        manifid: string, ARK NOID

        wagtail_field_names: list of field names (strings) stored in
        Wagtail database for a given collection

    Returns:
        Dictionary representing metadata to be displayed on collection
        object page.
    """
    dct = get_record_parsed(manifid, wagtail_field_names, modify=modify, func=func)
    try:
        if dct:
            main_output = {k: render_field(v) for k, v in dct.items()}
            add_extra_fields(manifid, main_output)
            return main_output
        else:
            return ""
    except (json.JSONDecodeError, simplejson.JSONDecodeError):
        return ""
