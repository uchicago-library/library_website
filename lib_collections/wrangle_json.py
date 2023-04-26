from collections import OrderedDict
import json
import requests
import urllib
import random

# default collection, for testing interactively
DEFAULT = "mlc"

# default collection group, for testing interactively
DEFGRP = "dma"


def open_json(filepath):
    f = open(filepath, "r")
    contents = f.read()
    f.close()
    return json.loads(contents)


class CleanData():

    def bindings(sparql):
        return sparql["results"]["bindings"]

    class KeyValue():

        def adjacent_key_value(keyField, valField, data):
            bs = CleanData.bindings(data)

            def each_pair(var):
                return (var[keyField]["value"], var[valField]["value"])
            return OrderedDict([ each_pair(pred) for pred in bs ])

        def downward_key_value(data):
            bs = CleanData.bindings(data)
            def each_pair(k,v):
                return (k, v["value"].split("|"))
            def nonempty(data):
                v = data["value"]
                unavailable = '(:unav)'
                return v and v != unavailable
            def each_binding(dct):
                alist = [ each_pair(k,v)
                          for (k,v) in dct.items()
                          if nonempty(v) ]
                return OrderedDict(alist)
            return [ each_binding(b)
                     for b in bs
                     if each_binding(b) ]

    adjacent_key_value = KeyValue.adjacent_key_value

    def getBrowseListContributors(data):
        return CleanData.adjacent_key_value("o", "s", data)

    def getBrowseListLocations(data):
        return CleanData.adjacent_key_value("prefLabel", "spatial", data)

    def getBrowseListLanguages(data):
        return CleanData.adjacent_key_value("code", "prefLabel", data)

    downward_key_value = KeyValue.downward_key_value

    def getItem(data):
        return CleanData.downward_key_value(data)

    class StraightUpList():

        def straight_up_list(fieldName, data, cleanup=lambda x : x):
            bs = CleanData.bindings(data)
            return [ cleanup(b[fieldName]["value"]) for b in bs ]

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
            cleaned = [ clean_url(u) for u in full_ark ]
            if cleaned:
                plucked = cleaned[0]
            else:
                plucked = []
            item["identifier"] = plucked
            return item
        return [ each_item(r) for r in results ]

    class Language():

        def contains_key(key):
            def partial(dct):
                return key in dct.keys()
            return partial

        def split_on(pred, lst):
            left = [ y for y in lst if pred(y) ]
            right = [ z for z in lst if not pred(z) ]
            return (left, right)

        # not using this yet, but I suspect we will need it
        def alternative_union(dct1, dct2):
            if dct1 == {}:
                return dct2
            elif dct2 == {}:
                return dct1
            else:
                left_half = { k:v
                              for (k, v) in dct1.items()
                              if k not in dct2}
                intersection = { u:(dct1[u] + dct2[u])
                                 for u in dct1
                                 if u in dct2 }
                right_half = { k:v
                               for (k,v) in dct2.items()
                               if k not in dct1 }
                return OrderedDict({**left_half, **intersection, **right_half})

    def getSeries(data):
        contains_key = CleanData.Language.contains_key
        split_on = CleanData.Language.split_on
        cleaned = CleanData.downward_key_value(data)
        (prefs, entry) = split_on(contains_key("prefLabel"), cleaned)
        # def clean_prefs(lst):
        #     cleaned = [ (d['languageRole'][0], d['prefLabel'])
        #                 for d in lst ]
        #     return dict(cleaned)
        # language = { "languageInfo" : clean_prefs(prefs) }
        # return OrderedDict({**entry[0], **language})
        return prefs

class URLs():

    class BaseURL():

        class MarkLogic():

            ML_HOST = "http://marklogic.lib.uchicago.edu"
            ML_PORT = 8031
            ML_PATH = "mainQuery.xqy?query="

            def assemble_url_prefix_full(host,
                                         collection,
                                         api_name, 
                                         port,
                                         path):
                parts = [
                    host,
                    ":",
                    str(port),
                    "/",
                    collection,
                    "/",
                    path,
                    api_name,
                ]
                return "".join(parts)

            def assemble_url_prefix(collection, api_name):
                return URLs.BaseURL.MarkLogic.assemble_url_prefix_full(
                    URLs.BaseURL.MarkLogic.ML_HOST,
                    collection,
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

        def getSeries(identifier="b20715n2p17r", collection=DEFAULT):
            print("QStrings: ", identifier)
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
            url_prefix = URLs.marklogic_base(collection, api_name)
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

    def getSeries(identifier="b20715n2p17r", collection=DEFAULT, curl=True):
        print("URLs identifier: ", identifier)
        params = URLs.QStrings.getSeries(identifier=identifier, collection=collection)
        print("URLS params: ", params)
        url = URLs.make_api_string(collection, "getSeries", params, curl)
        return url


class Api():

    def lookup(collection=DEFAULT, identifier="b2k40qk4wc8h", search=""):
        return {

            "getBrowseListContributors" : {
                "url" : URLs.getBrowseListContributors(collection, curl=False),
                "params" : URLs.QStrings.getBrowseListContributors(collection),
                "cleanup" : CleanData.getBrowseListContributors,
            },

            "getBrowseListLocations" : {
                "url" : URLs.getBrowseListLocations(collection, curl=False),
                "params" : URLs.QStrings.getBrowseListLocations(collection),
                "cleanup" : CleanData.getBrowseListLocations,
            },

            "getBrowseListLanguages" : {
                "url" : URLs.getBrowseListLanguages(collection, curl=False),
                "params" : URLs.QStrings.getBrowseListLanguages(collection),
                "cleanup" : CleanData.getBrowseListLanguages,
            },

            "getBrowseListDates" : {
                "url" : URLs.getBrowseListDates(collection, curl=False),
                "params" : URLs.QStrings.getBrowseListDates(collection),
                "cleanup" : CleanData.getBrowseListDates,
            },

            "getItem" : {
                "url" : URLs.getItem(identifier, collection, curl=False),
                "params" : URLs.QStrings.getItem(identifier, collection),
                "cleanup" : CleanData.getItem,
            },

            "getResultsByCreator" : {
                "url" : URLs.getResultsByCreator(search, collection, curl=False),
                "params" : URLs.QStrings.getResultsByCreator(search, collection),
                "cleanup" : CleanData.getResultsByCreator,
            },

            "getResultsByDate" : {
                "url" : URLs.getResultsByDate(search, collection, curl=False),
                "params" : URLs.QStrings.getResultsByDate(search, collection),
                "cleanup" : CleanData.getResultsByDate,
            },

            "getResultsByIdentifier" : {
                "url" : URLs.getResultsByIdentifier(identifier, collection, curl=False),
                "params" : URLs.QStrings.getResultsByIdentifier(identifier, collection),
                "cleanup" : CleanData.getResultsByIdentifier,
            },

            "getResultsByKeyword" : {
                "url" : URLs.getResultsByKeyword(search, collection, curl=False),
                "params" : URLs.QStrings.getResultsByKeyword(search, collection),
                "cleanup" : CleanData.getResultsByKeyword,
            },

            "getResultsByLanguage" : {
                "url" : URLs.getResultsByLanguage(search, collection, curl=False),
                "params" : URLs.QStrings.getResultsByLanguage(search, collection),
                "cleanup" : CleanData.getResultsByLanguage,
            },

            "getResultsByLocation" : {
                "url" : URLs.getResultsByLocation(search, collection, curl=False),
                "params" : URLs.QStrings.getResultsByLocation(search, collection),
                "cleanup" : CleanData.getResultsByLocation,
            },

            "getSeries" : {
                "url" : URLs.getSeries(identifier, collection, curl=False),
                "params" : URLs.QStrings.getSeries(identifier, collection),
                "cleanup" : CleanData.getSeries,
            },
            
        }

    class URLGet():

        def pull_from_url(url, func, params):
            print("URLGet params: ", params)
            response = requests.get(url, params)
            data = response.json()
            return func(data)

        def api_call(endpoint,
                     identifier="",
                     collection=DEFAULT,
                     search="",
                     raw=False):
            print("api_call identifier: ", identifier)
            lookup = Api.lookup(collection, identifier, search)[endpoint]
            params = lookup["params"]
            if raw:
                cleanup = lambda x : x
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

    def getSeries(identifier="b20715n2p17r",
                  collection=DEFAULT,
                  raw=False):
        print("Api identifier: ", identifier)
        return Api.api_call("getSeries",
                            collection=collection,
                            identifier=identifier,
                            raw=raw)

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
            return [ each_url(x["identifier"]["value"]) for x in bs ]
        return Api.URLGet.pull_from_url(base_url, cleanup, {})

    def gimme_some_noids(collection=DEFAULT):
        length = 70000
        start = random.randrange(0, length)
        end = start + 10
        return Utils.gimme_all_noids(collection)[start:end]

