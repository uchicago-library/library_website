import json
import pprint
import requests
import urllib.request

import xml.etree.cElementTree as ET

data = {
  'client_id': '344',
  'client_secret': '4c6060306c43233871a6f45a2b633e5f',
  'grant_type': 'client_credentials'
}

site_id = '1951'
key = 'dbc31802274b580fcc3056d55cc06720'

# get an access token.
r = requests.post('https://lgapi-us.libapps.com/1.2/oauth/token', data=data)
j = json.loads(r.text)
access_token = j['access_token']

# get a-z assets.
r = requests.get('https://lgapi-us.libapps.com/1.2/az', headers={'Authorization': 'Bearer ' + access_token})
j = json.loads(r.text)




