import re
import json
from library_website.settings.local import OWNCLOUD_USERNAME, OWNCLOUD_PASSWORD, OWNCLOUD_WEB_SERVICE
import owncloud
import os
import requests
from mvol_validator import mainvalidate
from random import shuffle

'''
This and cron_queue_er.py will be the two local scripts that should be put into cron.
They in turn depend on Keith's cai.json being updated in cron, to get accurate lists.
This should ideally be run as often as possible, but at least every minute. However,
it should not run if the previous run has not yet completed.

This function take all of the folders marked queue from the json lists, run them through the validator,
and based on the results mark them valid or invalid.
'''

def filterbottom(oc, p):
    '''
    Filters out folders that are not at the bottom level of the hierarchy
    '''
    if re.match('mvol/\d{4}/\d{4}/\d{4}/?$', p):
        return ('IIIF_Files/' + p, p)
    elif not p:
        return


def runutil(oc, file_info, result):
    '''
    Replaces queue sentinel flag with either valid, or invalid
    '''
    for entry in oc.list(file_info.get_path()):
        if entry.get_name() == 'queue':
            oc.delete(entry)
            os.utime(result)
            oc.put_file(file_info, result)
            break

username = OWNCLOUD_USERNAME
password = OWNCLOUD_PASSWORD
oc = owncloud.Client(OWNCLOUD_WEB_SERVICE)
oc.login(username, password)

r = requests.get('https://www2.lib.uchicago.edu/keith/tmp/cai.json')
r = r.json()
allqueues = r['queue']
allqueuesfiltered = []
for rt in allqueues:
    print(rt)
    allqueuesfiltered = allqueuesfiltered + [filterbottom(oc, rt[1])]
unknowns = []
for rt in allqueuesfiltered:
    if rt:
        print(rt[0])
        freshbatcherrors = mainvalidate(oc, rt[0])
        if not freshbatcherrors:
            runutil(oc, oc.file_info(rt[0]), "valid")
            print("no error")
        else:
            f = open("invalid", "w")
            for error in freshbatcherrors:
                print(error)
                if error[-22:] == "has an unknown error.\n":
                    unknowns.append(error)
                f.write(error)
            f.close()
            runutil(oc, oc.file_info(rt[0]), "invalid")

print("unknowns:\n")
for u in unknowns:
    print(u)
