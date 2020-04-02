import math
import requests


from json import JSONDecodeError

from library_website.settings.local import LIBCAL_KEY


def lookup_staff_ids():
    url = ("https://rooms.lib.uchicago.edu/1.0/" +
           "appointments/users?iid=482&key=%s") % LIBCAL_KEY
    req = requests.get(url)
    try:
        json = req.json()
        return {person['email']: person['id'] for person in json}
    # the wrong URL will not return JSON
    except JSONDecodeError:
        return None


def pad_empties(emails, ids):
    for email in emails:
        if email in ids.keys:
            pass
        else:
            ids[email] = None
            return ids
