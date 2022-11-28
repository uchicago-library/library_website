import owncloud
import os
import getpass
import sys
import re
import tempfile
import json
import random
from password import ocpassword
'''
This file builds json file from all owncloud directories, and based on commented out lines,
gives either all valids or in-syncs, or randoms valids and in-syncs or invalids and out-of-syncs
'''


def statusrecurse(start):
    if 'children' not in start:
        return (
            start['owncloud'][0],
            start['development'][0],
            start['production'][0])
    else:
        valids = []
        devs = []
        pros = []
        mostrecent = 0
        mostdev = 0
        mostpro = 0
        for child in start['children'].items():
            gift = statusrecurse(child[1])
            valids.append(gift[0])
            devs.append(gift[1])
            pros.append(gift[2])
            mostrecent = chxistnrecentnum(mostrecent, child[1]['owncloud'][1])
            mostdev = chxistnrecentnum(mostdev, child[1]['development'][1])
            mostpro = chxistnrecentnum(mostpro, child[1]['production'][1])
        first = "valid"
        second = "none"
        third = "none"
        if "invalid" in valids:
            first = "invalid"
        elif "valid" not in valids:
            first = "none"

        if "out-of-sync" in devs:
            second = "out-of-sync"
        elif "none" not in devs:
            second = "in-sync"
            start['development'][1] = mostdev

        if "out-of-sync" in pros:
            third = "out-of-sync"
        elif "none" not in pros:
            third = "in-sync"
            start['production'][1] = mostpro

        start['owncloud'][0] = first
        start['owncloud'][1] = mostrecent
        start['development'][0] = second
        start['production'][0] = third
        return(first, second, third)


def chxistnrecentnum(currtime, comparetime):
    # checks if two times exist and returns the larger
    if not comparetime == "none":
        if comparetime < currtime:
            return currtime
        else:
            return comparetime
    else:
        return currtime


def builddirectory(start, name, withchildren):

    name = name.replace("/", "-")
    validornot = random.randint(0, 1)
    firstdate = random.randint(0, 1227148486)
    if validornot:
        first = "valid"
        devearlylatenone = random.randint(0, 2)
        if devearlylatenone == 0:
            seconddate = random.randint(0, firstdate)
            second = "out-of-sync"
            proearlylate = random.randint(0, 1)
            if proearlylate == 0:
                third = "out-of-sync"
                thirddate = random.randint(0, firstdate)
            else:
                third = "none"
                thirddate = "none"
        elif devearlylatenone == 1:
            second = "in-sync"
            seconddate = random.randint(firstdate + 1, 1227148486)
            proearlylatenone = random.randint(0, 2)
            if proearlylatenone == 0:
                thirddate = random.randint(seconddate + 1, 1227148486)
                third = "in-sync"
            elif proearlylatenone == 1:
                thirddate = random.randint(0, firstdate)
                third = "out-of-sync"
            else:
                third = "none"
                thirddate = "none"
        else:
            second = "none"
            third = "none"
            seconddate = "none"
            thirddate = "none"
    else:
        first = "invalid"
        second = "none"
        third = "none"
        seconddate = "none"
        thirddate = "none"

    if withchildren:
        start[name] = {"owncloud": ["none", "none"],
                       "development": ["none", "none"],
                       "production": ["none", "none"],
                       "children": {}}
    else:
        start[name] = {"owncloud": [first, firstdate],
                       "development": [second, seconddate],
                       "production": [third, thirddate]}


def build(startfolder, namesofar, ocfolder, layer):
    # commented out lines determine whether just mvol/0004 is read, or
    # everything
    if layer != 2:
        for f in oc.list(ocfolder):
            tname = f.get_name()
            tname = namesofar + "/" + tname
            # if re.match('^/?IIIF_Files/mvol/0004(/\d{4}){0,2}/?$',
            # "IIIF_Files/" + tname):
            if re.match(
                '^/?IIIF_Files/mvol(/\d{4}){0,3}/?$',
                    "IIIF_Files/" + tname):
                builddirectory(startfolder['children'], tname, 1)
                build(startfolder['children'][tname.replace(
                    "/", "-")], tname, "IIIF_Files/" + tname, layer + 1)
    else:
        for f in oc.list(ocfolder):
            tname = f.get_name()
            tname = namesofar + "/" + tname
            # if re.match('^/?IIIF_Files/mvol/0004(/\d{4}){0,2}/?$',
            # "IIIF_Files/" + tname):
            if re.match(
                '^/?IIIF_Files/mvol(/\d{4}){0,3}/?$',
                    "IIIF_Files/" + tname):
                builddirectory(startfolder['children'], tname, 0)


if __name__ == '__main__':
    try:
        oc = owncloud.Client(os.environ['OWNCLOUD_SERVER'])
    except KeyError:
        sys.stderr.write("OWNCLOUD_SERVER environmental variable not set.\n")
        sys.exit()

    username = "ldr_oc_admin"
    password = ocpassword

    try:
        oc.login(username, password)
    except owncloud.HTTPResponseError:
        sys.stderr.write('incorrect WebDAV password.\n')
        sys.exit()
    mainfile = {}
    builddirectory(mainfile, "mvol", 1)
    build(mainfile['mvol'], "mvol", "IIIF_Files/mvol", 0)
    statusrecurse(mainfile['mvol'])
    with open('snar.json', 'w') as fp:
        json.dump(mainfile, fp)

    print("done")
