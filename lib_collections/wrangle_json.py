from collections import OrderedDict
import json
import requests
import urllib

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
                    "&",
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

            ARK_HOST = "http://ark.lib.uchicago.edu"
            ARK_PATH = "ark:61001"

            def assemble_url_prefix(host, path):
                def partial(noid):
                    parts = [
                        host,
                        "/",
                        path,
                        "/",
                        noid,
                    ]
                    return "".join(parts)
                return partial

            ark_base = assemble_url_prefix(ARK_HOST, ARK_PATH)

    marklogic_base = BaseURL.MarkLogic.assemble_url_prefix
    ark_base = BaseURL.Ark.ark_base

    class QueryStrings():

        def getBrowseListContributors(collection="mlc"):
            return { "collection" : collection }

        def getBrowseListLocations(collection="mlc"):
            return { "collection" : collection }

        def getBrowseListLanguages(collection="mlc"):
            return { "collection" : collection }

        def getBrowseListDates(collection="mlc"):
            return { "collection" : collection }

        def getItem(collection="mlc", noid="b2k40qk4wc8h"):
            return { "collection" : collection,
                     "identifier" : URLs.ark_base(noid), }

    getBrowseListContributors = QueryStrings.getBrowseListContributors
    getBrowseListLocations = QueryStrings.getBrowseListLocations
    getBrowseListLanguages = QueryStrings.getBrowseListLanguages
    getBrowseListDates = QueryStrings.getBrowseListDates
    getItem = QueryStrings.getItem

    class MakeURL():

        def make_api_string(collection, api_name, params):
            query_string = urllib.parse.urlencode(params)
            url_prefix = URLs.marklogic_base(collection, api_name)
            return url_prefix + query_string

    make_api_string = MakeURL.make_api_string
    
class Api():

    def lookup(collection="mlc", noid="b2k40qk4wc8h"):
        return {
            "getBrowseListContributors" : {
                "params" : URLs.getBrowseListContributors(collection),
                "cleanup" : CleanData.getBrowseListContributors,
            },
            "getBrowseListLocations" : {
                "params" : URLs.getBrowseListLocations(collection),
                "cleanup" : CleanData.getBrowseListLocations,
            },
            "getBrowseListLanguages" : {
                "params" : URLs.getBrowseListLanguages(collection),
                "cleanup" : CleanData.getBrowseListLanguages,
            },
            "getBrowseListDates" : {
                "params" : URLs.getBrowseListDates(collection),
                "cleanup" : CleanData.getBrowseListDates,
            },
            "getItem" : {
                "params" : URLs.getItem(collection, noid),
                "cleanup" : CleanData.getItem,
            },
        }

    class URLGet():

        def pull_from_url(url, func):
            response = requests.get(url)
            data = response.json()
            return func(data)

        def api_call(endpoint, collection="mlc", noid="b2k40qk4wc8h"):
            params = Api.lookup(collection, noid)[endpoint]["params"]
            cleanup = Api.lookup(collection, noid)[endpoint]["cleanup"]
            url = URLs.make_api_string(collection, endpoint, params)
            data = Api.pull_from_url(url, cleanup)
            return url
            # return data

    pull_from_url = URLGet.pull_from_url
    api_call = URLGet.api_call

    def getBrowseListContributors(collection="mlc", noid="b2k40qk4wc8h"):
        return Api.api_call("getBrowseListContributors")

    def getBrowseListLocations(collection="mlc", noid="b2k40qk4wc8h"):
        return Api.api_call("getBrowseListLocations")

    def getBrowseListLanguages(collection="mlc", noid="b2k40qk4wc8h"):
        return Api.api_call("getBrowseListLanguages")

    def getBrowseListDates(collection="mlc", noid="b2k40qk4wc8h"):
        return Api.api_call("getBrowseListDates")

    def getItem(collection="mlc", noid="b2k40qk4wc8h"):
        return Api.api_call("getItem")

    # def getBrowseListContributors(collection="mlc"):
    #     params = URLs.getBrowseListContributors(collection)
    #     cleanup = CleanData.getBrowseListContributors
    #     url = URLs.make_api_string(collection, "getBrowseListContributors", params)
    #     data = Api.pull_from_url(url, cleanup)
    #     return data
        
    # def getBrowseListLocations(collection="mlc"):
    #     params = URLs.getBrowseListLocations(collection)
    #     cleanup = CleanData.getBrowseListLocations
    #     url = URLs.make_api_string(collection, "getBrowseListLocations", params)
    #     data = Api.pull_from_url(url, cleanup)
    #     return data

    # def getBrowseListLanguages(collection="mlc"):
    #     params = URLs.getBrowseListLanguages(collection)
    #     cleanup = CleanData.getBrowseListLanguages
    #     url = URLs.make_api_string(collection, "getBrowseListLanguages", params)
    #     data = Api.pull_from_url(url, cleanup)
    #     return data

    # def getBrowseListDates(collection="mlc"):
    #     params = URLs.getBrowseListDates(collection)
    #     cleanup = CleanData.getBrowseListDates
    #     url = URLs.make_api_string(collection, "getBrowseListDates", params)
    #     data = Api.pull_from_url(url, cleanup)
    #     return data

getBrowseListContributors = Api.getBrowseListContributors
getBrowseListLocations = Api.getBrowseListLocations
getBrowseListDates = Api.getBrowseListDates
getBrowseListLanguages = Api.getBrowseListLanguages
getItem = Api.getItem

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

# make_api_string = URLs.MakeURL.make_api_string
# marklogic_base = URLs.marklogic_base
# ark_base = URLs.ark_base
# params = URLs.getItem()
