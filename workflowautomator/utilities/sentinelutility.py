import owncloud
import os
import getpass
import sys
import re
import tempfile
from library_website.settings import OWNCLOUD_USERNAME, OWNCLOUD_PASSWORD, OWNCLOUD_WEB_SERVICE
import argparse
import datetime

'''
Called by the Validate and Validate All buttons on the site, this makes folders ready if:
they are marked none,
they are marked invalid, or
they are marked valid, but the folder has been changed between now and the last
validation
'''
def get_mvol_mmdd_directories(oc, p):
    '''Get a list of mvol mmdd directories from a given path.
       Arguments:
       oc, an owncloud object.
       p, the directory path as a string, e.g. "IIIF_Files/mvol/0004/1930"
       Returns:
       a list of strings, paths to mmdd directories.
    '''
    if re.match('^/?IIIF_Files/mvol/\d{4}/\d{4}/\d{4}/?$', p):
        return [p]
    elif re.match('^/?IIIF_Files/mvol(/\d{4}){0,3}/?$', p):
        directories = []
        for e in oc.list(p):
            if e.is_dir():
                directories = directories + \
                    get_mvol_mmdd_directories(oc, e.path)
        return directories
    else:
        return []


def get_sentinel_files(oc, file_info):
    '''Get the sentinel files in a given mmdd directory.
       Arguments:
       oc, an owncloud object.
       file_info, an owncloud.FileInfo object describing an mmdd directory.
       Returns:
       a list of owncloud.FileInfo objects in this directory.
    '''
    sentinels = []
    goodforready = False
    for entry in oc.list(file_info.get_path()):
        if entry.get_name() in ('ready', 'queue', 'valid', 'invalid'):
            sentinels.append(oc.file_info(entry.path))
            if entry.get_name() == 'invalid':
              goodforready = True
            if entry.get_name() == 'valid':
              if entry.get_last_modified() < (file_info.get_last_modified() + datetime.timedelta(0,-20)):
                # last modified date is naturally a few seconds after valid's, this line avoids false issues
                # where valid appears out of sync
                goodforready = True
    if len(sentinels) == 0:
      goodforready = True
    return (sentinels, goodforready)


def runutil(oc, file_info, mode):
    '''
       Modify the sentinel files in a given mmdd directory.

       Arguments:
       oc, an owncloud object.
       file_info, an owncloud.FileInfo object describing an mmdd directory.
       mode, "addready"|"fix"|"deleteall".
       Side effect:
       manages sentinel files.
    '''
    sentinels = get_sentinel_files(oc, file_info)
    if mode == "addready" and sentinels[1] and len(sentinels[0]) <= 1 :
        for s in sentinels[0]:
            if s.get_name() in ('ready', 'queue', 'valid', 'invalid'):
                oc.delete(s)
        os.utime("workflowautomator/utilities/ready")
        oc.put_file(file_info, "workflowautomator/utilities/ready")
    elif mode == "fix" and len(sentinels[0]) > 1:
        for s in sentinels[0]:
            if s.get_name() in ('ready', 'queue', 'valid', 'invalid'):
                oc.delete(s)
    elif mode == "deleteall":
        for s in sentinels[0]:
            if s.get_name() in ('ready', 'queue', 'valid', 'invalid'):
                oc.delete(s)


def plant(directory, mode):
    oc = owncloud.Client(OWNCLOUD_WEB_SERVICE)
    oc.login(OWNCLOUD_USERNAME, OWNCLOUD_PASSWORD)

    for p in get_mvol_mmdd_directories(
        oc,
        ("/IIIF_Files/" +
         directory).replace(
            '-',
            '/')):
        print(p)
        runutil(oc, oc.file_info(p), mode)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "directory",
        help="e.g. mvol/0004/1930/0103")
    parser.add_argument(
        "mode", help='''addready to add ready to all empty folders,
                      fix to delete sentinel files from any folder with more than one,
                      deleteall to delete all sentinel files''')
    args = parser.parse_args()

    if args.mode not in ('addready', 'fix', 'deleteall'):
        sys.stderr.write("Mode is invalid, use addready, fix, or deleteall.\n")
        sys.exit()
    print("about to start")
    plant(args.directory, args.mode)
