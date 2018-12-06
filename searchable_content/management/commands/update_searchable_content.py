from django.core.management.base import BaseCommand
from searchable_content.models import SearchableContent
from wagtail.search import index
from library_website.settings.local import LIBGUIDES_CLIENT_ID, LIBGUIDES_CLIENT_SECRET, LIBGUIDES_API_OAUTH_TOKEN_ENDPOINT, LIBGUIDES_API_ASSETS_AZ_ENDPOINT, LIBGUIDES_API_GUIDES_ENDPOINT, LIBGUIDES_OAI_PMH_ENDPOINT 
 
import datetime 
import json
import pytz
import re
import requests
import sys
import urllib.request
import xml.etree.cElementTree as ET

def update_libguides_assets():
  """Load the assets from libguides into Wagtail as non-page objects that are
     available to the search index by using the libguides API. If records in 
     the libguides API are newer, update records in Wagtail. Delete records 
     that don't exist in the libguides API. 

     Arguments:
     none
 
     Returns: 
     none
  """

  access_token = json.loads(
    requests.post(
      LIBGUIDES_API_OAUTH_TOKEN_ENDPOINT,
      data = {
        'client_id': LIBGUIDES_CLIENT_ID,
        'client_secret': LIBGUIDES_CLIENT_SECRET,
        'grant_type': 'client_credentials'
      }
    ).text
  )['access_token']

  assets = json.loads(
    requests.get(
      LIBGUIDES_API_ASSETS_AZ_ENDPOINT,
      headers={'Authorization': 'Bearer ' + access_token}
    ).text
  )

  strip_tags = re.compile('<.*?>')

  identifiers = []

  for asset in assets:
    identifier = asset['id']
    identifiers.append(identifier)

    datestamp = pytz.utc.localize(datetime.datetime.strptime(asset['updated'], '%Y-%m-%d %H:%M:%S'))

    try:
      if SearchableContent.objects.get(identifier=identifier, tag='libguides-assets').datestamp == datestamp:
	# if the asset exists in Wagtail and is newer than or equal to the
	# date already present in the system, continue with the next asset.
        continue
    except:
      # if this asset doesn't exist in Wagtail, add it.
      pass

    record_url = asset['url']
    if record_url == '':
      continue

    if '/h/ahsi' in record_url:
      print('HERE IT IS!!!!!!')
      print(record_url)

    try:
      more_info = re.sub(strip_tags, ' ', asset['meta']['more_info'])
    except:
      more_info = ''

    try:
      SearchableContent.objects.update_or_create(
        identifier = identifier,
        title = asset['name'][:255],
        datestamp = datestamp,
        url = record_url,
        description = more_info,
        content = '',
        tag='libguides-assets'
      )
    except:
      pass

  # delete records that weren't present in the data.
  for searchable_content in SearchableContent.objects.filter(tag='libguides-assets'):
    if not searchable_content.identifier in identifiers:
      searchable_content.delete()

def update_libguides_guides():
  """Load the guides from libguides into Wagtail as non-page objects that are
     available to the search index by using the libguides API. If records in 
     the libguides API are newer, update records in Wagtail. Delete records 
     that don't exist in the libguides API. 

     Arguments:
     none
 
     Returns: 
     none
  """

  guides = json.loads(
    requests.get(
      LIBGUIDES_API_GUIDES_ENDPOINT
    ).text
  )

  identifiers = []

  for guide in guides:
    status_label = guide['status_label']
    if status_label != 'Published':
      continue

    identifier = guide['id']
    identifiers.append(identifier)

    datestamp = pytz.utc.localize(datetime.datetime.strptime(guide['updated'], '%Y-%m-%d %H:%M:%S'))

    try:
      if SearchableContent.objects.get(identifier=identifier, tag='libguides-guides').datestamp == datestamp:
	# if the guide exists in Wagtail and is newer than or equal to the
	# date already present in the system, continue with the next asset.
        continue
    except:
      # if this guide doesn't exist in Wagtail, add it.
      pass

    record_url = guide['url']
    if record_url == '':
      continue

    try:
      SearchableContent.objects.update_or_create(
        identifier = identifier,
        title = guide['name'][:255],
        datestamp = datestamp,
        url = record_url,
        description = guide['description'],
        content = '',
        tag='libguides-guides'
      )
    except:
      pass

  # delete records that weren't present in the data.
  for searchable_content in SearchableContent.objects.filter(tag='libguides-guides'):
    if not searchable_content.identifier in identifiers:
      searchable_content.delete()

def update_libguides_oai_pmh():
  """Load libguides into Wagtail as non-page objects that are available to the
     search index by iterating over records available via OAI-PMH. If records in 
     OAI-PMH are newer, update the record in Wagtail. Delete records in Wagtail
     that don't exist in OAI-PMH.

     Arguments:
     none
 
     Returns: 
     none
  """
  ns = {
    'oai_pmh': 'http://www.openarchives.org/OAI/2.0/',
    'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
    'dc': 'http://purl.org/dc/elements/1.1/'
  }

  identifiers = []

  # working from OAI-PMH data, create or update any necesary SearchableContent objects. 
  url = base_url = LIBGUIDES_OAI_PMH_ENDPOINT
 
  while True:
    root = ET.ElementTree(file=urllib.request.urlopen(url)).getroot()

    for record in root.findall('oai_pmh:ListRecords/oai_pmh:record', ns):
      r = record.find('oai_pmh:metadata/oai_dc:dc/dc:identifier', ns)
      if r == None:
         continue
      else:
         record_url = r.text
      if record_url == '':
        continue

      identifier = record.find('oai_pmh:header/oai_pmh:identifier', ns).text
      identifiers.append(identifier)

      datestamp = pytz.utc.localize(datetime.datetime.strptime(
        record.find('oai_pmh:header/oai_pmh:datestamp', ns).text,
        '%Y-%m-%dT%H:%M:%SZ'
      ))

      try:
        if SearchableContent.objects.get(identifier=identifier, tag='libguides-oai-pmh').datestamp == datestamp:
	  # if the asset exists in Wagtail and is newer than or equal to the
	  # date already present in the system, continue with the next asset.
          continue
      except:
        # if this asset doesn't exist in Wagtail, add it.
        pass

      try:    
        description = record.find(
          'oai_pmh:metadata/oai_dc:dc/dc:description',
          ns
        ).text
      except AttributeError:
        description = ''

      s = []
      for subject in record.findall('oai_pmh:metadata/oai_dc:dc/dc:subject', ns):
        if subject.text is not None:
          s.append(subject.text)
      subjects = ' '.join(s)

      try: 
        SearchableContent.objects.update_or_create(
          identifier = identifier,
          title = record.find('oai_pmh:metadata/oai_dc:dc/dc:title', ns).text[:255],
          datestamp = datestamp,
          url = record_url,
          description = description,
          content = subjects,
          tag='libguides-oai-pmh'
        )
      except:
        pass
  
    resumption_token = root.find(
      'oai_pmh:ListRecords/oai_pmh:resumptionToken',
      ns
    ).text

    if resumption_token:
      url = '{}&resumptionToken={}'.format(base_url, resumption_token)
    else:
      break

  # delete objects in the system that aren't present in OAI-PMH data.
  for searchable_content in SearchableContent.objects.filter(tag='libguides-oai-pmh'):
    if not searchable_content.identifier in identifiers:
      serachable_content.delete()

class Command(BaseCommand):
  def add_arguments(self, parser):
    parser.add_argument(
      '--clean',
      default=False,
      action='store_true'
    )
    parser.add_argument(
      '--libguides-assets',
      default=False,
      action='store_true'
    )
    parser.add_argument(
      '--libguides-guides',
      default=False,
      action='store_true'
    )
    parser.add_argument(
      '--libguides-oai-pmh',
      default=False,
      action='store_true'
    )
  def handle(self, *args, **options):
    if not (options['libguides_assets'] or options['libguides_guides']):
      print('Usage: python manage.py update_searchable_content [--clean] [--libguides-assets] [--libguides-guides] [--libguides-oai-pmh]')
      return
    if options['clean']:
      SearchableContent.objects.all().delete()
    if options['libguides_assets']:
      update_libguides_assets()
    if options['libguides_guides']:
      update_libguides_guides()
    if options['libguides_oai_pmh']:
      update_libguides_oai_pmh()
