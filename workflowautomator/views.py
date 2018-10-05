from django.shortcuts import render
from django.http import HttpResponse
import html
import json
import datetime
import time
import pytz
import requests
import owncloud
from library_website.settings import OWNCLOUD_USERNAME, OWNCLOUD_PASSWORD, OWNCLOUD_WEB_SERVICE
from workflowautomator.utilities import sentinelutility

# Create your views here.

breadcrumbsbase = [{
        "href": "/", "text": "Home"},
        {"href": "/workflowautomator", "text": "Emil Project Homepage"}]

def localizer(target, mode):
    '''Convert unix timestamps to localized python datetime.datetime objects.
        Arguments:
            target: if mode is "list": a list of tuples, where each tuple contains two elements:
                first, the state of a given item, and second, the time as
                seconds since the unix epoch. if mode is "hierarch": a single directory dict
            mode: "hierarch" or "list" indicating which part of the site is calling it, and which
                section of the function needs to be used
        Side effect:
        the second element of each tuple is converted to a python
            datetime.datetime object.
    '''
    timezone = pytz.timezone("UTC")
    if mode == "list":
        for t in target:
            t[0] = timezone.localize(datetime.datetime.fromtimestamp(t[0]))
            t[1] = '-'.join(t[1].split("/"))
    elif mode == "hierarch":
        for s in ('owncloud', 'development', 'production'):
            try:
                target[s][1] = timezone.localize(
                    datetime.datetime.fromtimestamp(target[s][1]))
            except Exception:
                pass


def about(request):
    context = {"breadcrumbs" : breadcrumbsbase}
    return render(request, 'workflowautomator/about.html', context)

def homepage(request):
    breadcrumbs = [{
        "href": "/",
        "text": "Home"
    }]
    context = {"breadcrumbs": breadcrumbs}
    return render(request, 'workflowautomator/homepage.html', context)

def errpage(request, mvolfolder_name):

    breadcrumbs = breadcrumbsbase + [{"href": "/workflowautomator/mvolreport", "text": "Mvol Report"},
        {"href": "/workflowautomator/mvolreport/invalid", "text": "invalid"}]

    oc = owncloud.Client(OWNCLOUD_WEB_SERVICE)
    oc.login(OWNCLOUD_USERNAME, OWNCLOUD_PASSWORD)
    newdirectorytitle = 'IIIF_Files/' + '/'.join(mvolfolder_name.split("-"))
    errors = []
    for entry in oc.list(oc.file_info(newdirectorytitle).get_path()):
        if entry.get_name() == 'invalid':
            errorsfile = oc.get_file(entry, 'workflowautomator/data/invalid')
            print(errorsfile)
            f = open("workflowautomator/data/invalid")
            for line in f:
                errors = errors + [line]
            f.close()
            break

    context = {'name': mvolfolder_name, 'errarray': errors, "breadcrumbs": breadcrumbs}
    return render(request, 'workflowautomator/errpage.html', context)

def prelistpage(request):
    r = requests.get('https://www2.lib.uchicago.edu/keith/tmp/cai.json')
    fjson = r.json()
    n = 5
    newfjson = {}
    for s in ("none", "ready", "queue", "valid", "invalid"):
        if fjson[s]:
            lengthx = len(fjson[s])
            fjson[s].sort(key = lambda x: x[1])
            newfjson[s] = (fjson[s][:n], lengthx > n, lengthx)
        else:
            newfjson[s] = ([], False, 0)
    for k, v in newfjson.items():
        localizer(v[0], "list")
    context = {"allists": newfjson, "breadcrumbs": breadcrumbsbase}
    return render(request, 'workflowautomator/prelistpage.html', context)

def listpage(request, status):
    breadcrumbs = breadcrumbsbase + [{"href": "/workflowautomator/mvolreport", "text": "Mvol Report"}]
    r = requests.get('https://www2.lib.uchicago.edu/keith/tmp/cai.json')
    fjson = r.json()
    localizer(fjson[status], "list")
    fjson[status].sort(key = lambda x: x[1])
    context = {"allists": fjson[status],
               "name": status, "breadcrumbs": breadcrumbs}
    return render(request, 'workflowautomator/listpage.html', context)

def setready(request):
    if request.method == 'POST':
        sentinelutility.plant(request.POST['name'], "addready")

    return HttpResponse('')

def hierarch(request, mvolfolder_name):

    def breadcrumbsmaker(mvolfolder_name):
        """Creates list of breadcrumb dicts, based on current location in
        the hierarchy on the site"""
        namesections = mvolfolder_name.split("-")
        breadcrumbs = []
        for i in range(0, len(namesections) - 1):
            breadcrumbs.append({
                "href": "/workflowautomator/" + '-'.join(namesections[: i + 1]),
                "text": namesections[i]})
        return breadcrumbs

    def get_mvol_data(jsondict, mvolfolder_name):
        """Gets the list of the mvolfolder's children as it exists in the json hierarchy"""
        namesections = mvolfolder_name.split("-")
        currdir = jsondict
        namesectone = namesections.pop(0)
        currdir = currdir[namesectone]
        for namesect in namesections:
            for child in currdir['children']:
                for key in child:
                    if namesect == key:
                        currdir = child[key]
        return currdir

    breadcrumbs = breadcrumbsbase + breadcrumbsmaker(mvolfolder_name)

    finalchunk = mvolfolder_name.split("-").pop()

    r = requests.get('https://www2.lib.uchicago.edu/keith/tmp/cai.json')
    prechildlist = get_mvol_data(r.json()["tree"], mvolfolder_name)['children']
    childlist = []
    check = html.unescape("&#10004;")
    ex = html.unescape("&#10006;")
    for childout in prechildlist:
        for key in childout:
            child = childout[key]
            # determines where checks, exes, and nones should go for each directory
            none = ""
            ready = ""
            queue = ""
            invalid = ""
            valid = ""
            prosync = "none"
            devsync = "none"
            currtime = child['owncloud'][1]
            if child['development'][0] == "in-sync":
                devsync = check
            elif child['development'][0] == "outtasync":
                devsync = ex
            if child['production'][0] == "in-sync":
                prosync = check
            elif child['production'][0] == "outtasync":
                prosync = ex
            if child['owncloud'][0] == "none":
                none = check
            elif child['owncloud'][0] == "ready":
                ready = check
            elif child['owncloud'][0] == "queue":
                queue = check
            elif child['owncloud'][0] == "invalid":
                invalid = check
            else:
                valid = check
            for s in ('production', 'development'):
                if child[s][1] == 0:
                    child[s][1] = "none"
            localizer(child, "hierarch")
            childlist.append((mvolfolder_name + "-" + key, child, valid, devsync, prosync, none, ready, queue, invalid))

    childlist.sort()
    oneupfrombottom = False
    if childlist:
        if not childlist[0][1]['children']:
            oneupfrombottom = True

    context = {'name': (mvolfolder_name, finalchunk),
               'children': childlist,
               'oneupfrombottom': oneupfrombottom,
               'breadcrumbs': breadcrumbs
               }

    return render(request, 'workflowautomator/mvolpagejson.html', context)
