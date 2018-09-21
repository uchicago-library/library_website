import argparse
import csv
import getpass
import os
import owncloud
import re
import sys
import io
import requests
from lxml import etree


def get_ancestor_fileinfo(oc, f, n):
    """Get an ancestor owncloud.FileInfo object.
       format (18|19|20)\d{2}

       Arguments:
       oc -- an owncloud object.
       f  -- an owncloud.FileInfo object.
       n  -- ancestor number. 1 = parent, 2 = grandparent, etc.

       Returns:
       an owncloud.FileInfo object for a directory n levels up in the filesystem.
    """

    pieces = f.get_path().split('/')
    while n:
        pieces.pop()
        n = n - 1

    return oc.file_info('/'.join(pieces))


def get_identifier_from_fileinfo(oc, f):
    """Get an identifier string from a fileinfo object that represents a mmdd directory.

       Arguments:
       oc -- an owncloud object.
       f  -- an owncloud.FileInfo object.

       Returns:
       an identifier string, e.g. 'mvol-0004-1930-0103'.
    """
    return '%s-%s-%s-%s' % (
        get_ancestor_fileinfo(oc, f, 3).get_name(),
        get_ancestor_fileinfo(oc, f, 2).get_name(),
        get_ancestor_fileinfo(oc, f, 1).get_name(),
        f.get_name()
    )


def validate_mvol_directory(oc, identifier, f):
    """Make sure that the great-grandparent of this directory is a folder called
       'mvol'.

       Arguments:
       oc         -- an owncloud object.
       identifier -- for error messages.
       f          -- an owncloud.FileInfo object for an mvol mmdd directory.

       Returns:
       A list of error messages, or an empty list.
    """

    if get_ancestor_fileinfo(oc, f, 3).get_name() == 'mvol':
        return []
    else:
        return [
            identifier +
            ' is contained in a great-grandparent folder that is not called "mvol".\n']


def validate_mvol_number_directory(oc, identifier, f):
    """Make sure that the grandparent of this directory is a four-digit mvol
       number, in the format /d{4}.

       Arguments:
       oc         -- an owncloud object.
       identifier -- for error messages.
       f          -- an owncloud.FileInfo object for an mvol mmdd directory.

       Returns:
       A list of error messages, or an empty list.
    """

    if re.match('^\d{4}$', get_ancestor_fileinfo(oc, f, 2).get_name()):
        return []
    else:
        return [
            identifier +
            ' is contained in a grandparent folder that is not a valid mvol number.\n']


def validate_year_directory(oc, identifier, f):
    """Make sure that the parent of this directory is a year folder, in the
       format (18|19|20)\d{2}

       Arguments:
       oc         -- an owncloud object.
       identifier -- for error messages.
       f          -- an owncloud.FileInfo object for an mvol mmdd directory.

       Returns:
       A list of error messages, or an empty list.
    """

    if re.match(
        '^(18|19|20)\d{2}$',
        get_ancestor_fileinfo(
            oc,
            f,
            1).get_name()):
        return []
    else:
        return [
            identifier +
            ' is contained in a parent folder that is not a valid year.\n']


def validate_date_directory(oc, identifier, f):
    """Make sure that this folder is in the format (0\d|1[012])[0123]\d.

       Arguments:
       oc         -- an owncloud object, or None, for testing.
       identifier -- for error messages.
       f          -- a file object that referrs to a mmdd directory.

       Returns:
       A list of error messages, or an empty list.
    """

    if re.match('^(0\d|1[012])[0123]\d$', f.get_name()):
        return []
    else:
        return [identifier + ' is not a valid mmdd folder name.\n']


def get_identifier(path):
    pieces = entry.path.split('/')
    if entry.path[-1:] == '/':
        pieces.pop()
    entry_filename = pieces.pop()

    identifier = []

    while True:
        piece = pieces.pop()
        if piece == 'mvol':
            identifier = [piece] + pieces[0:1]

    return '-'.join(identifier)


def validate_directory(oc, identifier, f, folder_name):
    """A helper function to validate ALTO, JPEG, and TIFF folders inside mmdd
       folders.

       Arguments:
       oc          -- an owncloud object.
       identifier  -- for error messages.
       f           -- a file object that referrs to a mmdd directory (the parent
                      of the ALTO, JPEG, or TIFF directory being validated.)
       folder_name -- the name of the folder: ALTO|JPEG|TIFF

       Returns:
       A list of error messages, or an empty list.
    """

    extensions = {
        'ALTO': 'xml',
        'JPEG': 'jpg',
        'TIFF': 'tif'
    }

    if folder_name not in extensions.keys():
        raise ValueError('unsupported folder_name.\n')

    errors = []

    filename_re = '^%s-%s-%s-%s_\d{4}\.%s$' % (
        get_ancestor_fileinfo(oc, f, 3).get_name(),
        get_ancestor_fileinfo(oc, f, 2).get_name(),
        get_ancestor_fileinfo(oc, f, 1).get_name(),
        f.get_name(),
        extensions[folder_name]
    )

    try:
        folder_f = oc.file_info(f.get_path() + '/' + folder_name)
        for entry in oc.list(folder_f.get_path()):
            if not entry.is_dir():
                if not re.match(filename_re, entry.get_name()):
                    errors.append(
                        identifier +
                        '/' +
                        folder_name +
                        ' contains incorrectly named files.\n')
                if entry.get_size() == 0:
                    errors.append(
                        identifier +
                        '/' +
                        folder_name +
                        ' contains a 0 byte file.\n')
    except owncloud.HTTPResponseError:
        errors.append(
            identifier +
            ' does not contain a ' +
            folder_name +
            ' folder.\n')

    return errors


def validate_alto_or_pos_directory(oc, identifier, f):
    """Validate that an ALTO or POS folder exists. Make sure it contains appropriate
       files.

       Arguments:
       oc          -- an owncloud object.
       identifier  -- for error messages.
       f           -- a file object that refers to a mmdd directory (the parent
                      of the directory being validated.)

       Returns:
       A list of error messages, or an empty list.
    """
    try:
        folder_f = oc.file_info(f.get_path() + '/' + 'ALTO')
        return validate_directory(oc, identifier, f, 'ALTO')
    except owncloud.HTTPResponseError:
        try:
          folder_f = oc.file_info(f.get_path() + '/' + 'POS')
          return spec_validate_pos_directory(oc, identifier + '/POS', folder_f)
        except owncloud.HTTPResponseError:
          return [identifier + ' does not contain a ALTO or POS folder.\n']

def spec_validate_pos_directory(oc, identifier, f):
  filename_re = '^\d*\.pos$'
  errors = []
  midlinespattern = re.compile('^((( *)?\d*\t){4}.*\n)?$')
  for entry in oc.list(f.get_path()):
      if not re.match(filename_re, entry.get_name()):
          errors.append(
              identifier + ' contains incorrectly named files.\n')
      file_object = io.BytesIO(oc.get_file_contents(entry))
      currline = file_object.readline().decode(errors = 'ignore')
      currlinenum = 1
      while currline:
          if not midlinespattern.fullmatch(currline):
                  errors.append(
                      identifier + '/' + entry.get_name() + 
                      ' has an error in line %d.\n' %
                      currlinenum)
          currline = file_object.readline().decode(errors = 'ignore')
          currlinenum += 1
  return errors

def validate_jpeg_directory(oc, identifier, f):
    """Validate that an JPEG folder exists. Make sure it contains appropriate
       files.

       Arguments:
       oc          -- an owncloud object.
       identifier  -- for error messages.
       f           -- a file object that refers to a mmdd directory (the parent
                      of the directory being validated.)

       Returns:
       A list of error messages, or an empty list.
    """
    return validate_directory(oc, identifier, f, 'JPEG')


def validate_tiff_directory(oc, identifier, f):
    """Validate that an TIFF folder exists. Make sure it contains appropriate
       files.

       Arguments:
       oc          -- an owncloud object.
       identifier  -- for error messages.
       f           -- a file object that refers to a mmdd directory (the parent
                      of the directory being validated.)

       Returns:
       A list of error messages, or an empty list.
    """
    return validate_directory(oc, identifier, f, 'TIFF')


def _validate_dc_xml_file(oc, identifier, file_object):
    """Make sure that a given dc.xml file is well-formed and valid, and that the
       date element is arranged as yyyy-mm-dd.

       Arguments:
       oc          -- an owncloud object, or None, for testing.
       identifier  -- for error messages.
       file_object -- a file object, the .dc.xml file.
    """
    dtdf = io.StringIO(      
        """<!ELEMENT metadata ((date, description, identifier, title)|
                    (date, description, title, identifier)|
                    (date, identifier, description, title)|
                    (date, identifier, title, description)|
                    (date, title, description, identifier)|
                    (date, title, identifier, description)|
                    (description, date, identifier, title)|
                    (description, date, title, identifier)|
                    (description, identifier, date, title)|
                    (description, identifier, title, date)|
                    (description, title, date, identifier)|
                    (description, title, identifier, date)|
                    (identifier, date, description, title)|
                    (identifier, date, title, description)|
                    (identifier, description, date, title)|
                    (identifier, description, title, date)|
                    (identifier, title, date, description)|
                    (identifier, title, description, date)|
                    (title, date, description, identifier)|
                    (title, date, identifier, description)|
                    (title, description, date, identifier)|
                    (title, description, identifier, date)|
                    (title, identifier, date, description)|
                    (title, identifier, description, date))>
                    <!ELEMENT title (#PCDATA)>
                    <!ELEMENT date (#PCDATA)>
                    <!ELEMENT identifier (#PCDATA)>
                    <!ELEMENT description (#PCDATA)>
                    """)
    dtd = etree.DTD(dtdf)
    dtdf.close()
    errors = []

    try:
        metadata = etree.fromstring(file_object.read())
        if not dtd.validate(metadata):
            errors.append(identifier + '.dc.xml is not valid.\n')
        else:
            datepull = etree.ElementTree(metadata).findtext("date")
            pattern = re.compile("^\d{4}(-\d{2})?(-\d{2})?")
            attemptmatch = pattern.fullmatch(datepull)
            if attemptmatch:
                sections = [int(s) for s in re.findall(r'\b\d+\b', datepull)]
                length = len(sections) 
                print(length) 
                if (sections[0] < 1700) | (sections[0] > 2100):
                    errors.append(
                        identifier + '.dc.xml has an incorrect year field.\n')
                if length > 1:  
                  if (sections[1] < 1) | (sections[1] > 12):
                      errors.append(identifier +
                                    '.dc.xml has an incorrect month field.\n')
                if length > 2:  
                  if (sections[2] < 1) | (sections[2] > 31):
                      errors.append(
                          identifier + '.dc.xml has an incorrect day field.\n')
            else:
                errors.append(identifier +
                              '.dc.xml has a date with a wrong format.\n')
    except etree.XMLSyntaxError as e:
        errors.append(identifier + '.dc.xml is not well-formed.\n')
        pass

    return errors


def validate_dc_xml(oc, identifier, file_info):
    """Make sure that a given dc.xml file is well-formed and valid, and that the
       date element is arranged as yyyy-mm-dd.

       Arguments:
       oc         -- an owncloud object, or None, for testing.
       identifier -- for error messages.
       file_info  -- a fileinfo object, the mmdd directory containing the .dc.xml
                     file.
    """
    try:
        file_object = io.BytesIO(oc.get_file_contents('{}/{}.dc.xml'.format(
            file_info.path, get_identifier_from_fileinfo(oc, file_info))))
        return _validate_dc_xml_file(oc, identifier, file_object)
    except owncloud.HTTPResponseError:
        return [identifier + '.dc.xml does not exist.\n']


def validate_mets_xml(oc, identifier, file_info):
    """Make sure that a given mets.xml file is well-formed and valid, and that the
       date element is arranged as yyyy-mm-dd.

       Arguments:
       oc         -- an owncloud object, or None, for testing.
       identifier -- for error messages.
       file_info  -- a fileinfo object, the mmdd directory containing the .mets.xml
    """
    try:
        file_object = io.BytesIO(oc.get_file_contents('{}/{}.mets.xml'.format(
            file_info.path, get_identifier_from_fileinfo(oc, file_info))))
        return _validate_mets_xml_file(oc, identifier, file_object)
    except owncloud.HTTPResponseError:
        return [identifier + '.mets.xml does not exist.\n']


def _validate_mets_xml_file(oc, identifier, file_object):
    """Make sure that a given mets file is well-formed and valid.

       Arguments:
       oc          -- an owncloud object, or None, for testing.
       identifier  -- for error messages.
       file_object -- a file object containing a mets.xml file.
    """
    errors = []

    # alternatively StringIO
    schemfd = open("mets.xsd.xml", 'r', encoding='utf8')
    schemdoc = etree.parse(schemfd)
    schemfd.close()
    xmlschema = etree.XMLSchema(schemdoc)

    try:
        fdoc = etree.parse(file_object).getroot()
        if not xmlschema.validate(fdoc):
            errors.append(
                identifier +
                '.mets.xml does not validate against schema.\n')
    except etree.XMLSyntaxError:
        errors.append(identifier + '.mets.xml is not a well-formed XML file.\n')
        pass

    return errors


def _validate_file_notempty(oc, identifier, file_object, file_format):
    """Make sure that a given file is not empty.

       Arguments:
       oc          -- an owncloud object, or None, for testing.
       identifier  -- for error messages.
       file_object -- a file object containing a mets.xml file.
       file_format -- .pdf, .struct.txt etc
    """
    errors = []

    file_object.seek(0, os.SEEK_END)
    size = file_object.tell()

    if not size:
        errors.append(identifier + file_format + ' is an empty file.\n')
    return errors


def validate_pdf(oc, identifier, file_info):
    """Make sure that a given .pdf file is well-formed and valid, and that the
       date element is arranged as yyyy-mm-dd.

       Arguments:
       oc         -- an owncloud object, or None, for testing.
       identifier -- for error messages.
       file_info  -- a fileinfo object, the mmdd directory containing the struct.txt
    """
    try:
        file_object = io.BytesIO(oc.get_file_contents('{}/{}.pdf'.format(
            file_info.path, get_identifier_from_fileinfo(oc, file_info))))
        return _validate_file_notempty(oc, identifier, file_object, ".pdf")
    except owncloud.HTTPResponseError:
        return [identifier + '.pdf does not exist.\n']


def validate_txt(oc, identifier, file_info):
    """Make sure that a given .txt file is well-formed and valid, and that the
       date element is arranged as yyyy-mm-dd.

       Arguments:
       oc         -- an owncloud object, or None, for testing.
       identifier -- for error messages.
       file_info  -- a fileinfo object, the mmdd directory containing the struct.txt
    """
    try:
        file_object = io.BytesIO(oc.get_file_contents('{}/{}.txt'.format(
            file_info.path, get_identifier_from_fileinfo(oc, f))))
        return _validate_file_notempty(oc, identifier, file_object, ".txt")
    except owncloud.HTTPResponseError:
        return [identifier + '.txt does not exist.\n']


def validate_struct_txt(oc, identifier, file_info):
    """Make sure that a given struct.txt file is well-formed and valid, and that the
       date element is arranged as yyyy-mm-dd.

       Arguments:
       oc         -- an owncloud object, or None, for testing.
       identifier -- for error messages.
       file_info  -- a fileinfo object, the mmdd directory containing the struct.txt
    """
    try:
        file_object = io.BytesIO(oc.get_file_contents('{}/{}.struct.txt'.format(
            file_info.path, get_identifier_from_fileinfo(oc, file_info))))
        return _validate_struct_txt_file(
            oc, identifier, file_object)
    except owncloud.HTTPResponseError:
        return [identifier + '.struct.txt does not exist.\n']


def _validate_struct_txt_file(oc, identifier, file_object):
    """Make sure that a given struct.txt is valid. It should be tab-delimited
       data, with a header row. Each record should contains a field for object,
       page and milestone.

       Arguments:
       oc          -- an owncloud object, or None, for testing.
       identifier  -- for error messages.
       file_object -- a file object containing a struct.txt file.
    """
    errors = []

    num_lines = sum(1 for line in file_object)
    
    f = open("holdit.txt", "w")
    file_object.seek(0,0)
    currline = file_object.readline().decode()
    while currline:
      f.write(currline)
      currline = file_object.readline().decode()
    f.close()

    file_object = open("holdit.txt", "r")
    
    file_object.seek(0, 0)
    firstline = file_object.readline()
    firstlinepattern = re.compile("^object\tpage\tmilestone\n")
    if not firstlinepattern.fullmatch(firstline):
        errors.append(
            identifier +
            '.struct.txt has an error in the first line.\n')
    currlinenum = 2
    midlinespattern = re.compile('^\d{8,9}\t(\d{1,3}|(.*))?\t?(.*)?\n')
    finlinepattern = re.compile('^\d{8,9}(\t\d{1,3}|(.*))?\t?(.*)?')
    currline = file_object.readline()
    while(currline):
        if not midlinespattern.fullmatch(currline):
            if not ((currlinenum == num_lines)
                    and finlinepattern.fullmatch(currline)):
                errors.append(
                    identifier +
                    '.struct.txt has an error in line %d.\n' %
                    currlinenum)
        currlinenum += 1
        currline = file_object.readline()

    return errors


def finalcheck(directory):
    """Make sure that a passing directory does not ultimately fail validation
      for an unknown reason

       Arguments:
       directory --- name of the mvol folder being tested
    """
    freshdirectorypieces = directory.split("/")
    freshdirectorypieces.pop(0)
    freshdirectory = '-'.join(freshdirectorypieces)
    if freshdirectory[-1] == "-":
      freshdirectory = freshdirectory[:-1]
    print(freshdirectory)
    url = "https://digcollretriever.lib.uchicago.edu/projects/" + \
        freshdirectory + "/ocr?jpg_width=0&jpg_height=0&min_year=0&max_year=0"
    r = requests.get(url)
    if r.status_code != 200:
        return [directory + ' has an unknown error.\n']
    else:
        try:
            fdoc = etree.fromstring(r.content)
            return []
        except Exception:
            return [directory + ' has an unknown error.\n']


def mainvalidate(oc, directory):
    errors = []
    try:
        f = oc.file_info(directory)
        identifier = get_identifier_from_fileinfo(oc, f)
        errors = errors + validate_mvol_directory(oc, identifier, f)
        errors = errors + validate_mvol_number_directory(oc, identifier, f)
        if re.match('IIIF_Files/mvol/0004/', directory):
          errors = errors + validate_year_directory(oc, identifier, f)
          errors = errors + validate_date_directory(oc, identifier, f)
        errors = errors + validate_alto_or_pos_directory(oc, identifier, f)
        errors = errors + validate_jpeg_directory(oc, identifier, f)
        errors = errors + validate_tiff_directory(oc, identifier, f)
        errors = errors + validate_dc_xml(oc, identifier, f)
        #errors = errors + validate_mets_xml(oc, identifier, f)
        errors = errors + validate_pdf(oc, identifier, f)
        errors = errors + validate_struct_txt(oc, identifier, f)
        if not errors:
            errors = finalcheck(directory)
    except owncloud.HTTPResponseError:
        errors = errors + [directory + ' does not exist.\n']

    return errors
