from collections import OrderedDict
import json

def openJson(filepath):
    f = open(filepath, "r")
    contents = f.read()
    f.close()
    return json.loads(contents)

class KeyValue():

    def keyValue(keyField, valField, data):
        bindings = data["results"]["bindings"]
        def eachPair(var):
            return (var[keyField]["value"], var[valField]["value"])
        return OrderedDict([ eachPair(pred) for pred in bindings ])

    def getBrowseListContributors(data):
        return keyValue("o", "s", data)

    def getBrowseListLocations(data):
        return keyValue("prefLabel", "spatial", data)

    def getBrowseListLanguages(data):
        return keyValue("prefLabel", "code", data)

getBrowseListContributors = KeyValue.getBrowseListContributors
getBrowseListLocations = KeyValue.getBrowseListLocations
getBrowseListLanguages = KeyValue.getBrowseListLanguages

class StraightUpList():

    def straightUpList(fieldName, data):
        bindings = data["results"]["bindings"]
        return [ x[fieldName]["value"] for x in bindings ]

    def getBrowseListDates(data):
        return straightUpList("date")

getBrowseListDates = StraightUpList.getBrowseListDates
