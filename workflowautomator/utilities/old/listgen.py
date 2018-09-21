import json
import random
'''
This file generates five lists of directories for the categories valid,
invalid, ready, queue, and none, by loading the json file storing
the sample data for the mvol directory section. The data is processed and
saved in a new json file so it can be used in the mvol directory report
section.

'''


def directorytrawl(start):
    nograndchildren = True
    for child in start.items():
        if 'children' in child[1]:
            nograndchildren = False
    if nograndchildren:
        for child in start.items():
            if child[1]['owncloud'][0] == "valid":
                share = random.randint(0, 4)
                if share == 0:
                    valay.append((child[0], child[1]['owncloud'][1]))
                elif share == 1:
                    valay.append((child[0], child[1]['owncloud'][1]))
                elif share == 2:
                    queay.append((child[0], child[1]['owncloud'][1]))
                elif share == 3:
                    queay.append((child[0], child[1]['owncloud'][1]))
                else:
                    nonay.append((child[0], child[1]['owncloud'][1]))
            elif child[1]['owncloud'][0] == "invalid":
                share = random.randint(0, 4)
                if share == 0:
                    invay.append((child[0], child[1]['owncloud'][1]))
                elif share == 1:
                    invay.append((child[0], child[1]['owncloud'][1]))
                elif share == 2:
                    reaay.append((child[0], child[1]['owncloud'][1]))
                elif share == 3:
                    reaay.append((child[0], child[1]['owncloud'][1]))
                else:
                    nonay.append((child[0], child[1]['owncloud'][1]))
    else:
        for child in start.items():
            directorytrawl(child[1]["children"])


if __name__ == '__main__':

    with open('snar.json', "r") as jsonfile:
        fjson = json.load(jsonfile)

    currdir = fjson
    nonay = []
    reaay = []
    queay = []
    valay = []
    invay = []

    directorytrawl(fjson["mvol"]["children"])
    prepmulti = {"none": nonay, "ready": reaay, "queue": queay, "valid": valay,
                 "invalid": invay}

    with open('listsnar.json', 'w') as fp:
        json.dump(prepmulti, fp)
