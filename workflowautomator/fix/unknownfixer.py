import os
import owncloud
import requests
from library_website.settings import OWNCLOUD_USERNAME, OWNCLOUD_WEB_SERVICE
try:
    from library_website.settings import OWNCLOUD_PASSWORD
except(ImportError):
    OWNCLOUD_PASSWORD = os.environ['OWNCLOUD_PASSWORD']

"""Running the process function on an onwcloud directory, e.g. "IIIF_Files/mvol/0500/0020/0011",
that has failed validation for an unknown reason, should give tell you which specific file or folder
is causing the validation to fail"""

def saveall(outerdirectory):
    """This function saves a copy of everything in the owncloud directory, so that it can be restored
    a file at a time to see which one fails the validator, and also so the folder can be restored
    in its entirety at the end"""
    pieces = outerdirectory.split("/")
    lastpiece = pieces.pop()
    os.mkdir(lastpiece)
    os.chdir(lastpiece)
    for entry in oc.list(oc.file_info(outerdirectory).get_path()):
        if entry.is_dir():
            saveall(outerdirectory + '/' + entry.get_name())
        else:
            oc.get_file(outerdirectory + '/' + entry.get_name())
    os.chdir("..")

def restoreall(outerdirectory):
    """This function restores the copied owncloud directory, and also renames the default
    'good' files to their original names, so that the process function runs correctly 
    the next time it's called"""
    outerouter = outerdirectory[:-5]
    oc.delete(outerdirectory)
    oc.put_directory(outerouter, outerdirectory)
    os.remove(outerdirectory)
    extensions = [".dc.xml", ".mets.xml", ".pdf", ".struct.txt", ".txt"]
    myfiles = os.listdir('.')
    for filex in myfiles:
        origlen = len(extensions)
        i = 0
        while i < origlen:
            if filex[-length:] == extension:
                os.rename(filex, "a" + extension)
                i = origlen
            i += 1

def replaceall(outerdirectory):
    """This function goes through the owncloud directory and replaces every file or folder with its
    default 'good' version that is stored locally. The 'good' versions need to be renamed to match
    the files they are replacing"""
    extensions = ["ALTO", "POS", "TIFF", "JPEG", ".dc.xml", ".mets.xml", ".pdf", ".struct.txt", ".txt"]
    for entry in oc.list(oc.file_info(outerdirectory).get_path()):
        currentryname = entry.get_name()
        print("replacing " + currentryname)
        origlen = len(extensions)
        i = 0
        while i < origlen:
            tryx = singlereplace(entry, extensions[i], outerdirectory)
            if tryx == True:
                extensions.pop(i)
                print(currentryname + " has been replaced")
                i = origlen
            i += 1
        if entry:
            print(currentryname + " was not expected, and is being deleted")
            oc.delete(entry)

def singlereplace(entry, extension, outerdirectory):
    """This is the function that is called numerous times by replaceall, and does the replacing
    for a single one of the files, if it matches one of the names or file extensions we're expecting"""
    length = len(extension)
    if entry.get_name()[-length:] == extension:
        oc.delete(entry)
        if extension in ("ALTO", "POS", "TIFF", "JPEG"):
            newname = extension
        else:
            pieces = outerdirectory.split("/")
            pieces.pop(0)
            freshdirectory = "-".join(pieces)
            newname = freshdirectory + extension
            os.rename("a" + extension, newname)
        oc.put_file(outerdirectory, newname)
        return True

def testall(outerdirectory):
    """This function calls singletest on every entry in the owncloud directory"""
    extensions = ["ALTO", "POS", "TIFF", "JPEG", ".dc.xml", ".mets.xml", ".pdf", ".struct.txt", ".txt"]
    for entry in oc.list(oc.file_info(outerdirectory).get_path()):
        currentryname = entry.get_name()
        print("testing " + currentryname)
        origlen = len(extensions)
        while i < origlen:
            tryx = singletest(entry, extensions[i], outerdirectory)
            if tryx[0] == True:
                extensions.pop(i)
                i = origlen + 1
                print(currentryname + " passed")   
            if tryx[0] == False:
                return tryx[1]
            i += 1
    return "No issue found :/"

def singletest(entry, extension, outerdirectory):
    """This function replaces a single file/directory on owncloud, currently the 'good' version, with
    the original version, and then sees if running the validator succeeds or not"""
    length = len(extension)
    origname = entry.get_name()
    pieces = outerdirectory.split("/")
    lastpiece = pieces.pop()
    if origname[-length:] == extension:
        if entry.is_dir(): 
            oc.put_directory(outerdirectory, lastpiece + "/" + origname)
        else: 
            oc.put_file(outerdirectory, lastpiece + "/" + origname)
        if freshdirectory[-1] == "-":
            freshdirectory = freshdirectory[:-1]
        url = "https://digcollretriever.lib.uchicago.edu/projects/" + \
            freshdirectory + "/ocr?jpg_width=0&jpg_height=0&min_year=0&max_year=0"
        r = requests.get(url)
        if r.status_code != 200:
            text = newname + "has an error"
            return (False, text)
        try:
            fdoc = etree.fromstring(r.content)
            return (True, "")
        except Exception:
            text = newname + "has an error"
            return (False, text)

def process(outerdirectory):
    """This function saves the owncloud directory, replaces its contents, tests each content,
    restores everything to how it was, and then reports which file failed"""
    #saveall(outerdirectory)
    print("save done")
    replaceall(outerdirectory)
    print("replacing all is done")
    finaloutput = test(outerdirectory)
    print("testing is complete")
    #restoreall(outerdirectory)
    print("restoration complete")
    print(finaloutput)

oc = owncloud.Client(OWNCLOUD_WEB_SERVICE)
oc.login(OWNCLOUD_USERNAME, OWNCLOUD_PASSWORD)
process("IIIF_Files/mvol/0500/0020/0011")
