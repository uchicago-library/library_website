import json
# import simplejson
import re
import random

import requests
from library_website.settings import (
    MARKLOGIC_LDR_PASSWORD,
    MARKLOGIC_LDR_USER,
    MARKLOGIC_LDR_URL,
    SPARQL_ROOT
)
from requests.auth import HTTPBasicAuth
from lib_collections.utils import GeneralPurpose
import urllib
from collections import OrderedDict
from base.utils import compose, concat, const


def sp_query(manifid: str) -> str:
    """
    Construct SparQL query from collection object NOID.

    Args:
        manifid: string, ARK NOID

    Returns:
        SparQL query in the form of a string
    """
    return '''SELECT ?coverage ?creator ?date ?description ?format ?identifier ?publisher ?rights ?subject ?title ?type ?spatial ?ClassificationLcc ?Local
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
              }}'''.format(manifid, SPARQL_ROOT)


def get_raw_record(manifid: str,
                   modify=GeneralPurpose.noop,
                   func=GeneralPurpose.identity) -> dict:
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
            headers={'Content-type': 'text/turtle'},
            params={'query': sp_query(manifid)},
            url=MARKLOGIC_LDR_URL + '/sparql',
        )
        modify(r)
        j = json.loads(r.content.decode('utf-8'))
        return func(j)
    except requests.exceptions.RequestException:
        return ''


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
        dct: Dictionary representing result of Mark Logic query,

        wagtail_field_names: list of field names (strings) stored in
        Wagtail database for a given collection

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
    except (KeyError, IndexError):
        return ''


def get_record_no_parsing(manifid: str,
                          wagtail_field_names: list,
                          modify=GeneralPurpose.noop,
                          func=GeneralPurpose.identity) -> dict:
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
        return ''


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
        string: string containing metadata

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


def get_record_parsed(manifid: str,
                      wagtail_field_names: list,
                      modify=GeneralPurpose.noop,
                      func=GeneralPurpose.identity) -> dict:
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
    dct = get_record_no_parsing(
        manifid, wagtail_field_names, modify=modify, func=func)
    if dct:
        return {k: brackets_parse(v) for k, v in dct.items()}
    else:
        return ''


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


def add_extra_fields(manifid: str,
                     dct: dict) -> dict:
    """
    Add 'parent collection' and 'permanent url' to the end of a list
    of metadata fields.  (We do this on every object page.)

    Args:
        manifid: string, ARK NOID

    Returns:
        Nothing; mutates the input dictionary
    """
    ark_base = 'https://www.lib.uchicago.edu/ark:/61001/'
    dct['Collection'] = 'Social Scientists Map Chicago'
    dct['Permanent URL'] = ark_base + manifid


def get_record_for_display(manifid: str,
                           wagtail_field_names: list,
                           modify=GeneralPurpose.noop,
                           func=GeneralPurpose.identity) -> dict:
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
    dct = get_record_parsed(manifid, wagtail_field_names,
                            modify=modify, func=func)
    try:
        if dct:
            main_output = {k: render_field(v) for k, v in dct.items()}
            add_extra_fields(manifid, main_output)
            return main_output
        else:
            return ''
    except (json.JSONDecodeError
            # , simplejson.JSONDecodeError
            ):
        return ''


# BEGIN WRANGLE_JSON CODE (MT May 2023)


# default collection, for testing interactively
DEFAULT = "mlc"
# default metadata fields to display; these are the ones for the MLC demo
DEFAULT_FIELDS = ['Alternative',
                  'DmaIdentifier',
                  'Title',
                  'Creator',
                  'Language',
                  'Spatial',
                  'Date',
                  'Description',]

# default collection group, for testing interactively
DEFGRP = "dma"


class CleanData():

    def bindings(sparql):
        return sparql["results"]["bindings"]

    class KeyValue():

        def adjacent_key_value(keyField, valField, data):
            bs = CleanData.bindings(data)

            def each_pair(var):
                return (var[keyField]["value"],
                        var[valField]["value"])
            return OrderedDict([each_pair(pred) for pred in bs])

        def downward_key_value(data):
            bs = CleanData.bindings(data)

            def each_pair(k, v):
                return (k, v["value"].split("|"))

            def nonempty(data):
                v = data["value"]
                unavailable = '(:unav)'
                return v and v != unavailable

            def each_binding(dct):
                alist = [each_pair(k, v)
                         for (k, v) in dct.items()
                         if nonempty(v)]
                return OrderedDict(alist)

            return [each_binding(b)
                    for b in bs
                    if each_binding(b)]

    adjacent_key_value = KeyValue.adjacent_key_value

    def getBrowseListContributors(data):
        return CleanData.adjacent_key_value("o", "s", data)

    def getBrowseListLocations(data):
        return CleanData.adjacent_key_value("spatial", "prefLabel", data)

    def getBrowseListLanguages(data):
        return CleanData.adjacent_key_value("code", "prefLabel", data)

    downward_key_value = KeyValue.downward_key_value

    def getItem(data):
        return CleanData.downward_key_value(data)

    class StraightUpList():

        def straight_up_list(fieldName, data, cleanup=lambda x: x):
            bs = CleanData.bindings(data)
            return [cleanup(b[fieldName]["value"]) for b in bs]

    straight_up_list = StraightUpList.straight_up_list

    def getBrowseListDates(data):
        return CleanData.straight_up_list("date", data)

    class Ark():

        def extract_noid(arkurl):
            return arkurl.split("/")[-1]

    def getResultsByCreator(data):
        return CleanData.straight_up_list(
            "resource",
            data,
            cleanup=CleanData.Ark.extract_noid
        )

    getResultsByDate = getResultsByCreator
    getResultsByKeyword = getResultsByCreator
    getResultsByLanguage = getResultsByCreator
    getResultsByLocation = getResultsByCreator

    def getResultsByIdentifier(data):
        results = CleanData.downward_key_value(data)

        def each_item(item):
            full_ark = item["identifier"]

            def clean_url(url):
                return url.split("/")[-1]
            cleaned = [clean_url(u) for u in full_ark]
            if cleaned:
                plucked = cleaned[0]
            else:
                plucked = []
            item["identifier"] = plucked
            return item
        return [each_item(r) for r in results]

    class Language():

        def contains_key(key):
            def partial(dct):
                return key in dct.keys()
            return partial

        def split_on(pred, lst):
            left = [y for y in lst if pred(y)]
            right = [z for z in lst if not pred(z)]
            return (left, right)

        # not using this yet, but I suspect we will need it
        def alternative_union(dct1, dct2):
            if dct1 == {}:
                return dct2
            elif dct2 == {}:
                return dct1
            else:
                left_half = {k: v
                             for (k, v) in dct1.items()
                             if k not in dct2}
                intersection = {u: (dct1[u] + dct2[u])
                                for u in dct1
                                if u in dct2}
                right_half = {k: v
                              for (k, v) in dct2.items()
                              if k not in dct1}
                return OrderedDict({**left_half, **intersection, **right_half})


    def getSeries(data):
        cleaned = CleanData.downward_key_value(data) 
        series = cleaned[0]

        def adjust_metadata_key(string):
            if string.lower() == "primary":
                return "primaryLanguage"
            elif string.lower() == "subject":
                return "subjectLanguage"
            else:
                return string
        
        def each_language(colon_str):
            [k, v] = colon_str.split(':')
            new_k = adjust_metadata_key(k.lower())
            return (new_k, [v])

        languages = series["languages"]
        alist = [each_language(l) for l in languages ]
        return OrderedDict(series, **dict(alist))
        # languages = dict(prepped)
        # series["languages"] = languages
        # series["language"] = languages["primary"]

        # return series

    # getSeries = getSeries_pipe


def split_on(pred, lst):
    left = [y for y in lst if pred(y)]
    right = [z for z in lst if not pred(z)]
    return (left, right)


class URLs():

    class BaseURL():

        class MarkLogic():

            ML_HOST = "http://marklogic.lib.uchicago.edu"
            ML_PORT = 8031
            ML_PATH = "main.xqy?query="
            ML_GROUP = "dma"

            def assemble_url_prefix_full(host,
                                         collection_group,
                                         api_name, 
                                         port,
                                         path):
                parts = [
                    host,
                    ":",
                    str(port),
                    "/",
                    collection_group,
                    "/",
                    path,
                    api_name,
                ]
                return "".join(parts)

            def assemble_url_prefix(api_name):
                return URLs.BaseURL.MarkLogic.assemble_url_prefix_full(
                    URLs.BaseURL.MarkLogic.ML_HOST,
                    URLs.BaseURL.MarkLogic.ML_GROUP,
                    api_name,
                    URLs.BaseURL.MarkLogic.ML_PORT,
                    URLs.BaseURL.MarkLogic.ML_PATH
                )
            
        class Ark():

            ARK_HOST = "https://ark.lib.uchicago.edu"
            ARK_PATH = "ark:61001"

            def assemble_url_prefix(host, path):
                def partial(identifier):
                    parts = [
                        host,
                        "/",
                        path,
                        "/",
                        identifier,
                    ]
                    return "".join(parts)
                return partial

            ark_base = assemble_url_prefix(ARK_HOST, ARK_PATH)

    marklogic_base = BaseURL.MarkLogic.assemble_url_prefix
    ark_base = BaseURL.Ark.ark_base

    class QStrings():

        def getBrowseListContributors(collection=DEFAULT):
            return { "collection" : collection }

        def getBrowseListLocations(collection=DEFAULT):
            return { "collection" : collection }

        def getBrowseListLanguages(collection=DEFAULT):
            return { "collection" : collection }

        def getBrowseListDates(collection=DEFAULT):
            return { "collection" : collection }

        def getItem(identifier="b2k40qk4wc8h", collection=DEFAULT):
            return { "collection" : collection,
                     "identifier" : URLs.ark_base(identifier), }

        def getResultsByCreator(search="mcquown", collection=DEFAULT):
            return { "collection" : collection,
                     "search" : search, }

        def getResultsByDate(search="1971", collection=DEFAULT):
            return { "collection" : collection,
                     "search" : search, }

        def getResultsByIdentifier(identifier="b2k40qk4wc8h", collection=DEFAULT):
            return { "collection" : collection,
                     "identifier" : URLs.ark_base(identifier), }

        def getResultsByKeyword(search="andrade", collection=DEFAULT):
            return { "collection" : collection,
                     "search" : search, }

        def getResultsByLanguage(search="tzotzil", collection=DEFAULT):
            return { "collection" : collection,
                     "search" : search, }

        def getResultsByLocation(search="yucatan", collection=DEFAULT):
            return { "collection" : collection,
                     "search" : search, }

        def getSeries(identifier="b2pz3jc17901", collection=DEFAULT):
            return { "collection" : collection,
                     "identifier" : URLs.ark_base(identifier), }


    class MakeURL():

        def make_api_string(collection, api_name, params, curl=True):
            unquote = urllib.parse.unquote
            urlencode = urllib.parse.urlencode
            def serialize(params):
                return urlencode(params)
                # toggle this for debugging
                # return unquote(urlencode(params))
            if curl:
                query_string = "&" + serialize(params)
            else:
                query_string = ""
            url_prefix = URLs.marklogic_base(api_name)
            return url_prefix + query_string

    make_api_string = MakeURL.make_api_string

    def getBrowseListContributors(collection=DEFAULT, curl=True):
        params = URLs.QStrings.getBrowseListContributors(collection=collection)
        url = URLs.make_api_string(collection,
                                   "getBrowseListContributors",
                                   params,
                                   curl)
        return url

    def getBrowseListLocations(collection=DEFAULT, curl=True):
        params = URLs.QStrings.getBrowseListLocations(collection=collection)
        url = URLs.make_api_string(collection,
                                   "getBrowseListLocations",
                                   params,
                                   curl)
        return url

    def getBrowseListLanguages(collection=DEFAULT, curl=True):
        params = URLs.QStrings.getBrowseListLanguages(collection=collection)
        url = URLs.make_api_string(collection,
                                   "getBrowseListLanguages",
                                   params,
                                   curl)
        return url

    def getBrowseListDates(collection=DEFAULT, curl=True):
        params = URLs.QStrings.getBrowseListDates(collection=collection)
        url = URLs.make_api_string(collection,
                                   "getBrowseListDates",
                                   params,
                                   curl)
        return url

    def getItem(identifier="b2k40qk4wc8h", collection=DEFAULT, curl=True):
        params = URLs.QStrings.getItem(identifier=identifier, collection=collection)
        url = URLs.make_api_string(collection, "getItem", params, curl)
        return url

    def getResultsByCreator(search="mcquown", collection=DEFAULT, curl=True):
        params = URLs.QStrings.getResultsByCreator(search=search, collection=collection)
        url = URLs.make_api_string(collection, "getResultsByCreator", params, curl)
        return url

    def getResultsByDate(search="1971", collection=DEFAULT, curl=True):
        params = URLs.QStrings.getResultsByCreator(search=search, collection=collection)
        url = URLs.make_api_string(collection, "getResultsByDate", params, curl)
        return url

    def getResultsByIdentifier(identifier="b2k40qk4wc8h", collection=DEFAULT, curl=True):
        params = URLs.QStrings.getResultsByIdentifier(identifier=identifier, collection=collection)
        url = URLs.make_api_string(collection, "getResultsByIdentifier", params, curl)
        return url

    def getResultsByKeyword(search="andrade", collection=DEFAULT, curl=True):
        params = URLs.QStrings.getResultsByKeyword(search=search, collection=collection)
        url = URLs.make_api_string(collection, "getResultsByKeyword", params, curl)
        return url

    def getResultsByLanguage(search="tzotzil", collection=DEFAULT, curl=True):
        params = URLs.QStrings.getResultsByLanguage(search=search, collection=collection)
        url = URLs.make_api_string(collection, "getResultsByLanguage", params, curl)
        return url

    def getResultsByLocation(search="yucatan", collection=DEFAULT, curl=True):
        params = URLs.QStrings.getResultsByLocation(search=search, collection=collection)
        url = URLs.make_api_string(collection, "getResultsByLocation", params, curl)
        return url

    def getSeries(identifier="b2pz3jc17901", collection=DEFAULT, curl=True):
        params = URLs.QStrings.getSeries(identifier=identifier, collection=collection)
        url = URLs.make_api_string(collection, "getSeries", params, curl)
        return url


class Api():

    def lookup(collection=DEFAULT, identifier="b2k40qk4wc8h", search="", curl=False):
        return {

            "getBrowseListContributors" : {
                "url" : URLs.getBrowseListContributors(collection, curl=curl),
                "params" : URLs.QStrings.getBrowseListContributors(collection),
                "cleanup" : CleanData.getBrowseListContributors,
            },

            "getBrowseListLocations" : {
                "url" : URLs.getBrowseListLocations(collection, curl=curl),
                "params" : URLs.QStrings.getBrowseListLocations(collection),
                "cleanup" : CleanData.getBrowseListLocations,
            },

            "getBrowseListLanguages" : {
                "url" : URLs.getBrowseListLanguages(collection, curl=curl),
                "params" : URLs.QStrings.getBrowseListLanguages(collection),
                "cleanup" : CleanData.getBrowseListLanguages,
            },

            "getBrowseListDates" : {
                "url" : URLs.getBrowseListDates(collection, curl=curl),
                "params" : URLs.QStrings.getBrowseListDates(collection),
                "cleanup" : CleanData.getBrowseListDates,
            },

            "getItem" : {
                "url" : URLs.getItem(identifier, collection, curl=curl),
                "params" : URLs.QStrings.getItem(identifier, collection),
                "cleanup" : CleanData.getItem,
            },

            "getResultsByCreator" : {
                "url" : URLs.getResultsByCreator(search, collection, curl=curl),
                "params" : URLs.QStrings.getResultsByCreator(search, collection),
                "cleanup" : CleanData.getResultsByCreator,
            },

            "getResultsByDate" : {
                "url" : URLs.getResultsByDate(search, collection, curl=curl),
                "params" : URLs.QStrings.getResultsByDate(search, collection),
                "cleanup" : CleanData.getResultsByDate,
            },

            "getResultsByIdentifier" : {
                "url": URLs.getResultsByIdentifier(identifier, collection, curl=curl),
                "params": URLs.QStrings.getResultsByIdentifier(identifier, collection),
                "cleanup": CleanData.getResultsByIdentifier,
            },

            "getResultsByKeyword": {
                "url": URLs.getResultsByKeyword(search, collection, curl=curl),
                "params": URLs.QStrings.getResultsByKeyword(search, collection),
                "cleanup": CleanData.getResultsByKeyword,
            },

            "getResultsByLanguage": {
                "url": URLs.getResultsByLanguage(search, collection, curl=curl),
                "params": URLs.QStrings.getResultsByLanguage(search, collection),
                "cleanup": CleanData.getResultsByLanguage,
            },

            "getResultsByLocation": {
                "url": URLs.getResultsByLocation(search, collection, curl=curl),
                "params": URLs.QStrings.getResultsByLocation(search, collection),
                "cleanup": CleanData.getResultsByLocation,
            },

            "getSeries" : {
                "url": URLs.getSeries(identifier, collection, curl=curl),
                "params": URLs.QStrings.getSeries(identifier, collection),
                "cleanup": CleanData.getSeries,
            },

        }

    class URLGet():

        def pull_from_url(url, func, params):
            response = requests.get(url, params)
            data = response.json()
            return func(data)

        def api_call(endpoint,
                     identifier="",
                     collection=DEFAULT,
                     search="",
                     raw=False,
                     curl=False):
            lookup = Api.lookup(collection, identifier, search, curl)[endpoint]
            params = lookup["params"]
            if raw:
                cleanup = lambda x: x
            else:
                cleanup = lookup["cleanup"]
            url = lookup["url"]
            data = Api.pull_from_url(url, cleanup, params)
            return data

    pull_from_url = URLGet.pull_from_url
    api_call = URLGet.api_call

    def getBrowseListContributors(collection=DEFAULT, raw=False):
        return Api.api_call("getBrowseListContributors",
                            collection=collection,
                            raw=raw)

    def getBrowseListLocations(collection=DEFAULT, raw=False):
        return Api.api_call("getBrowseListLocations",
                            collection=collection,
                            raw=raw)

    def getBrowseListLanguages(collection=DEFAULT, raw=False):
        return Api.api_call("getBrowseListLanguages",
                            collection=collection,
                            raw=raw)

    def getBrowseListDates(collection=DEFAULT, raw=False):
        return Api.api_call("getBrowseListDates",
                            collection=collection,
                            raw=raw)

    def getItem(identifier="b2k40qk4wc8h", collection=DEFAULT, raw=False):
        return Api.api_call("getItem",
                            collection=collection,
                            identifier=identifier,
                            raw=raw)

    def getResultsByCreator(search="mcquown", collection=DEFAULT, raw=False):
        return Api.api_call("getResultsByCreator",
                            collection=collection,
                            search=search,
                            raw=raw)

    def getResultsByDate(search="1971", collection=DEFAULT, raw=False):
        return Api.api_call("getResultsByDate",
                            collection=collection,
                            search=search,
                            raw=raw)

    def getResultsByIdentifier(identifier="b2k40qk4wc8h",
                               collection=DEFAULT,
                               raw=False):
        return Api.api_call("getResultsByIdentifier",
                            collection=collection,
                            identifier=identifier,
                            raw=raw)

    def getResultsByKeyword(search="andrade", collection=DEFAULT, raw=False):
        return Api.api_call("getResultsByKeyword",
                            collection=collection,
                            search=search,
                            raw=raw)

    def getResultsByLanguage(search="tzotzil", collection=DEFAULT, raw=False):
        return Api.api_call("getResultsByLanguage",
                            collection=collection,
                            search=search,
                            raw=raw)

    def getResultsByLocation(search="yucatan", collection=DEFAULT, raw=False):
        return Api.api_call("getResultsByLocation",
                            collection=collection,
                            search=search,
                            raw=raw)

    # TODO: currently throws an exception if you don't give it a
    # proper series noid; we should fix that
    def getSeries(identifier="b2pz3jc17901",
                  collection=DEFAULT,
                  raw=False):
        return Api.api_call("getSeries",
                            collection=collection,
                            identifier=identifier,
                            raw=raw)


class Wagtail():

    class GetSeries():

        def rdf_map(field, f):
            def partial(dct):
                current = dct[field]
                dct[field] = [f(x) for x in current]
                return dct
            return partial

        def fix_language(collection):
            def partial(dct):
                try:
                    code = dct["language"]
                    code_dictionary = Api.getBrowseListLanguages(
                        collection=collection
                    )
                    language = code_dictionary[code]
                    dct["language"] = language
                    return dct
                except KeyError:
                    return dct
            return partial

        def lowercase_first(string):
            if string:
                return string[0].lower() + string[1:]
            else:
                string

        def adjust_fields(field_names=DEFAULT_FIELDS):
            def partial(json_obj):
                lowercase_first = Wagtail.GetSeries.lowercase_first
                if field_names:
                    alist = [(x, "".join(v))
                             for x in field_names
                             for k, v in json_obj.items()
                             if (lowercase_first(x), v) == (k, v)]
                return OrderedDict(alist)
            return partial

        # TODO: have this replace location atomic thingy number with
        # actual location string
        def fix_everything(dct, collection=DEFAULT,
                           field_names=DEFAULT_FIELDS):
            fix_language = Wagtail.GetSeries.fix_language
            adjust_fields = Wagtail.GetSeries.adjust_fields
            fix = compose(
                fix_language(collection),
                adjust_fields(field_names),
            )
            return fix(dct)

        class ItemListing():

            def build_item_listing(parts):
                extract_noid = CleanData.Ark.extract_noid
                noids = [extract_noid(n) for n in parts]
                raw_items = concat([Api.getItem(i) for i in noids])
                descriptions = concat([i["description"] for i in raw_items])
                items = list(map(lambda d: ("", d), descriptions))
                return items

        def getSeries(identifier="b2pz3jc17901",
                      field_names=DEFAULT_FIELDS,
                      collection=DEFAULT,
                      raw=False):
            fix_everything = Wagtail.GetSeries.fix_everything
            build_item_listing = (Wagtail
                                  .GetSeries
                                  .ItemListing.build_item_listing)
            first_pass = Api.getSeries(identifier, collection, raw)
            series = fix_everything(first_pass, field_names=field_names)
            parts = first_pass["hasParts"]
            items = build_item_listing(parts)
            return (series, items)

    getSeries = GetSeries.getSeries

class Validation():

    def injection_safe(id):
        """
        Check that URL route ends in a well-formed NOID.  This is mostly
        just a simple safeguard against possible SparQL injection
        attacks.

        Args:
            Candidate NOID

        Returns:
            Boolean

        """
        length_ok = len(id) >= 1 and len(id) <= 30
        alphanum = id.isalnum()
        return length_ok and alphanum


class Utils():

    def gimme_all_noids(collection=DEFAULT):
        host = URLs.BaseURL.MarkLogic.ML_HOST
        port = URLs.BaseURL.MarkLogic.ML_PORT
        path = "identifiers.xqy?query()"
        parts = [
            host,
            ":",
            str(port),
            "/",
            collection,
            "/",
            path,
        ]
        base_url = "".join(parts)

        def cleanup(data):
            bs = CleanData.bindings(data)

            def each_url(url):
                return url.split("/")[-1]
            return [each_url(x["identifier"]["value"]) for x in bs]
        return Api.URLGet.pull_from_url(base_url, cleanup, {})

    def gimme_some_noids(collection=DEFAULT):
        length = 70000
        start = random.randrange(0, length)
        end = start + 10
        return Utils.gimme_all_noids(collection)[start:end]


def preview(x, amount=1500):
    print(json.dumps(x, indent=4)[:amount])
