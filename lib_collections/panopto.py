import requests
import urllib

example_ark = 'https://ark.lib.uchicago.edu/ark:61001/b25m5d94m413'


class Player():

    def ark_to_panopto(ark_url):
        req = requests.head(ark_url, allow_redirects=True)
        percent_url = req.url
        return urllib.parse.parse_qs(urllib.parse.urlparse(urllib.parse.parse_qs(urllib.parse.urlparse(percent_url).query)['ReturnUrl'][0]).query)["id"][0]
