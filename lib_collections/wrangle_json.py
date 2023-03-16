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

    class KeyValue():

        def key_value(keyField, valField, data):
            bindings = data["results"]["bindings"]
            def each_pair(var):
                return (var[keyField]["value"], var[valField]["value"])
            return OrderedDict([ each_pair(pred) for pred in bindings ])

    key_value = KeyValue.key_value
    
    def getBrowseListContributors(data):
        return CleanData.key_value("o", "s", data)

    def getBrowseListLocations(data):
        return CleanData.key_value("prefLabel", "spatial", data)

    def getBrowseListLanguages(data):
        return CleanData.key_value("code", "prefLabel", data)

    class StraightUpList():

        def straight_up_list(fieldName, data):
            bindings = data["results"]["bindings"]
            return [ x[fieldName]["value"] for x in bindings ]

    straight_up_list = StraightUpList.straight_up_list

    def getBrowseListDates(data):
        return CleanData.straight_up_list("date", data)
    
class Api():

    ML_HOST = "http://marklogic.lib.uchicago.edu"
    ML_PORT = 8031
    ML_PATH = "/mlc/mainQuery.xqy?query="

    class BaseURL():
        
        def assemble_url_prefix_full(host, api_name, port, path):
            parts = [
                host,
                ":",
                str(port),
                path,
                api_name,
                "&",
            ]
            return "".join(parts)

        def assemble_url_prefix(api_name):
            return Api.BaseURL.assemble_url_prefix_full(
                Api.ML_HOST,
                api_name,
                Api.ML_PORT,
                Api.ML_PATH
            )

    assemble_url_prefix = BaseURL.assemble_url_prefix

    class QueryStrings():

        def getBrowseListContributors(collection):
            return { "collection" : collection }

        def getBrowseListLocations(collection):
            return { "collection" : collection }

        def getBrowseListLanguages(collection):
            return { "collection" : collection }

        def getBrowseListDates(collection):
            return { "collection" : collection }

    class URLGet():

        def pull_from_url(url, func):
            response = requests.get(url)
            data = response.json()
            return func(data)

        def make_api_string(api_name, params):
            query_string = urllib.parse.urlencode(params)
            url_prefix = Api.assemble_url_prefix(api_name)
            return url_prefix + query_string

    pull_from_url = URLGet.pull_from_url
    make_api_string = URLGet.make_api_string

    def getBrowseListContributors(collection):
        params = Api.QueryStrings.getBrowseListContributors(collection)
        cleanup = CleanData.getBrowseListContributors
        url = Api.make_api_string("getBrowseListContributors", params)
        data = Api.pull_from_url(url, cleanup)
        return data
        
    def getBrowseListLocations(collection):
        params = Api.QueryStrings.getBrowseListLocations(collection)
        cleanup = CleanData.getBrowseListLocations
        url = Api.make_api_string("getBrowseListLocations", params)
        data = Api.pull_from_url(url, cleanup)
        return data

    def getBrowseListLanguages(collection):
        params = Api.QueryStrings.getBrowseListLanguages(collection)
        cleanup = CleanData.getBrowseListLanguages
        url = Api.make_api_string("getBrowseListLanguages", params)
        data = Api.pull_from_url(url, cleanup)
        return data

    def getBrowseListDates(collection):
        params = Api.QueryStrings.getBrowseListDates(collection)
        cleanup = CleanData.getBrowseListDates
        url = Api.make_api_string("getBrowseListDates", params)
        data = Api.pull_from_url(url, cleanup)
        return data

getBrowseListContributors = Api.getBrowseListContributors
getBrowseListLocations = Api.getBrowseListLocations
getBrowseListDates = Api.getBrowseListDates
getBrowseListLanguages = Api.getBrowseListLanguages
