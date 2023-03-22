from collections import OrderedDict
import json
import requests
import urllib
import random

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

        def straight_up_list(fieldName, data):
            bs = CleanData.bindings(data)
            return [ b[fieldName]["value"] for b in bs ]

    straight_up_list = StraightUpList.straight_up_list

    def getBrowseListDates(data):
        return CleanData.straight_up_list("date", data)

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

        def getBrowseListContributors(collection="mlc"):
            return { "collection" : collection }

        def getBrowseListLocations(collection="mlc"):
            return { "collection" : collection }

        def getBrowseListLanguages(collection="mlc"):
            return { "collection" : collection }

        def getBrowseListDates(collection="mlc"):
            return { "collection" : collection }

        def getItem(identifier="b2k40qk4wc8h", collection="mlc"):
            return { "collection" : collection,
                     "identifier" : URLs.ark_base(identifier), }

    class MakeURL():

        def make_api_string(collection, api_name, params, curl=True):
            if curl:
                query_string = "&" + urllib.parse.unquote(urllib.parse.urlencode(params))
            else:
                query_string = ""
            url_prefix = URLs.marklogic_base(collection, api_name)
            return url_prefix + query_string

    make_api_string = MakeURL.make_api_string

    def getBrowseListContributors(collection="mlc", curl=True):
        params = URLs.QStrings.getBrowseListContributors(collection)
        url = URLs.make_api_string(collection,
                                   "getBrowseListContributors",
                                   params,
                                   curl)
        return url

    def getBrowseListLocations(collection="mlc", curl=True):
        params = URLs.QStrings.getBrowseListLocations(collection)
        url = URLs.make_api_string(collection,
                                   "getBrowseListLocations",
                                   params,
                                   curl)
        return url

    def getBrowseListLanguages(collection="mlc", curl=True):
        params = URLs.QStrings.getBrowseListLanguages(collection)
        url = URLs.make_api_string(collection,
                                   "getBrowseListLanguages",
                                   params,
                                   curl)
        return url

    def getBrowseListDates(collection="mlc", curl=True):
        params = URLs.QStrings.getBrowseListDates(collection)
        url = URLs.make_api_string(collection,
                                   "getBrowseListDates",
                                   params,
                                   curl)
        return url

    def getItem(identifier="b2k40qk4wc8h", collection="mlc", curl=True):
        params = URLs.QStrings.getItem(identifier, collection)
        url = URLs.make_api_string(collection, "getItem", params, curl)
        return url
    
class Api():

    def lookup(collection="mlc", identifier="b2k40qk4wc8h"):
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
        }

    class URLGet():

        def pull_from_url(url, func, params):
            response = requests.get(url, params)
            data = response.json()
            return func(data)

        def api_call(endpoint, collection="mlc", identifier="b2k40qk4wc8h"):
            lookup = Api.lookup(collection, identifier)[endpoint]
            params = lookup["params"]
            cleanup = lookup["cleanup"]
            url = lookup["url"]
            data = Api.pull_from_url(url, cleanup, params)
            return data

    pull_from_url = URLGet.pull_from_url
    api_call = URLGet.api_call

    def getBrowseListContributors(collection="mlc"):
        return Api.api_call("getBrowseListContributors", collection)

    def getBrowseListLocations(collection="mlc"):
        return Api.api_call("getBrowseListLocations", collection)

    def getBrowseListLanguages(collection="mlc"):
        return Api.api_call("getBrowseListLanguages", collection)

    def getBrowseListDates(collection="mlc"):
        return Api.api_call("getBrowseListDates", collection)

    def getItem(identifier="b2k40qk4wc8h", collection="mlc"):
        return Api.api_call("getItem", collection, identifier)

class Utils():

    def gimme_all_noids(collection="mlc"):
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

    def gimme_some_noids(collection="mlc"):
        length = 70000
        start = random.randrange(0, length)
        end = start + 10
        return Utils.gimme_all_noids(collection)[start:end]

        

# getBrowseListContributors = CleanData.getBrowseListContributors
# getBrowseListLocations = CleanData.getBrowseListLocations
# getBrowseListDates = CleanData.getBrowseListDates
# getBrowseListLanguages = CleanData.getBrowseListLanguages
# getItem = CleanData.getItem

# getBrowseListContributors = URLs.getBrowseListContributors
# getBrowseListLocations = URLs.getBrowseListLocations
# getBrowseListDates = URLs.getBrowseListDates
# getBrowseListLanguages = URLs.getBrowseListLanguages
# getItem = URLs.getItem

# getBrowseListContributors = URLs.QStrings.getBrowseListContributors
# getBrowseListLocations = URLs.QStrings.getBrowseListLocations
# getBrowseListDates = URLs.QStrings.getBrowseListDates
# getBrowseListLanguages = URLs.QStrings.getBrowseListLanguages
# getItem = URLs.QStrings.getItem

getBrowseListContributors = Api.getBrowseListContributors
getBrowseListLocations = Api.getBrowseListLocations
getBrowseListDates = Api.getBrowseListDates
getBrowseListLanguages = Api.getBrowseListLanguages
getItem = Api.getItem

