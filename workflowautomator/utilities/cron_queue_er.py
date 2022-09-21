import re
import json
from library_website.settings import OWNCLOUD_USERNAME, OWNCLOUD_WEB_SERVICE
import owncloud
import os
import requests
try:
    from library_website.settings import OWNCLOUD_PASSWORD
except(ImportError):
    OWNCLOUD_PASSWORD = os.environ['OWNCLOUD_PASSWORD']
'''
This and cron_valid_er.py will be the two local scripts that should be put into cron.
They in turn depend on Keith's cai.json being updated in cron, to get accurate lists.
This should ideally be run as often as possible, but at least every minute. However,
it should not run if the previous run has not yet completed.

This function will check the lists for all of the folders marked ready, and remark them 
to queue.
'''
def filterbottom(oc, p):
    '''
    Filters out folders that are not at the bottom level of the hierarchy
    '''
    print(p)
    if re.match('mvol/\d{4}/\d{4}/\d{4}/?$', p):
        return 'IIIF_Files/' + p

def runutil(oc, file_info):
    '''
    Replaces ready sentinel flag with queue
    '''
    for entry in oc.list(file_info.get_path()):
        if entry.get_name() == 'ready':
            oc.delete(entry)
            os.utime("queue")
            oc.put_file(file_info, "queue")
            break

oc = owncloud.Client(OWNCLOUD_WEB_SERVICE)
oc.login(OWNCLOUD_USERNAME, OWNCLOUD_PASSWORD)

r = requests.get('https://www2.lib.uchicago.edu/keith/tmp/cai.json')
r = r.json()
allreadies = r['ready']

allreadiesfiltered = []
for rt in allreadies:
    allreadiesfiltered = allreadiesfiltered + [filterbottom(oc, rt)]

for rt in allreadiesfiltered:
    runutil(oc, oc.file_info(rt))
