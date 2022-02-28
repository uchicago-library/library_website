import json

import requests

from django.conf import settings

TIMEOUT = 2

GENERIC_HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'X-Okapi-Tenant': '%s' % settings.FOLIO_TENANT
}


def get_auth():
    """
    Authenticate and get auth token from Folio API.

    Returns:
        dict, with auth token.
    """
    data = {"x-okapi-token": '', 'refreshtoken': ''}
    try:
        payload = '{"username": "%s", "password": "%s"}' % (
            settings.FOLIO_USERNAME, settings.FOLIO_PASSWORD
        )
        response = requests.post(
            settings.FOLIO_BASE_URL + '/authn/login',
            headers=GENERIC_HEADERS,
            data=payload,
            timeout=TIMEOUT
        )
        if response.status_code != 201:
            return data
        return {
            "x-okapi-token": response.headers['x-okapi-token'],
            'refreshtoken': response.headers['refreshtoken']
        }
    except (
        requests.exceptions.Timeout, json.decoder.JSONDecodeError,
        requests.exceptions.ConnectionError
    ):
        pass
    return data


def get_instances(bib, token):
    """
    Queries the Folio instance storage API.

    Args:
        bib: string, bib number.

        token: string, token from get_auth dict.

    Returns:
        dict
    """
    if not bib:
        return dict()
    try:
        q = "(hrid==%s)" % bib
        headers = GENERIC_HEADERS
        headers.update({'X-Okapi-Token': token})
        url = settings.FOLIO_BASE_URL + '/instance-storage/instances?query=%s' % q
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        return json.loads(response.content)['instances'][0]
    except (
        requests.exceptions.Timeout, json.decoder.JSONDecodeError,
        requests.exceptions.ConnectionError, IndexError
    ):
        return dict()


def get_holdings(instance_id, token):
    """
    Queries the Folio holdings storage API.

    Args:
        instance_id: string, instance id.

        token: string, token from get_auth dict.

    Returns:
        dict
    """
    if not instance_id:
        return dict()
    try:
        q = '(instanceId=="' + instance_id + '" NOT discoverySuppress==true)'
        headers = GENERIC_HEADERS
        headers.update({'X-Okapi-Token': token})
        response = requests.get(
            settings.FOLIO_BASE_URL + '/holdings-storage/holdings?query=%s' % q,
            headers=headers,
            timeout=TIMEOUT
        )
        return json.loads(response.content)
    except (
        requests.exceptions.Timeout, json.decoder.JSONDecodeError,
        requests.exceptions.ConnectionError
    ):
        return dict()


def get_item(barcode, token):
    """
    Queries the Folio item storage API.

    Args:
        barcode: string

        token: string, token from get_auth dict

    Returns:
        dict
    """
    if barcode and token:
        try:
            q = '(barcode=' + barcode + ' NOT discoverySuppress==true)'
            headers = GENERIC_HEADERS
            headers.update({'X-Okapi-Token': token})
            url = settings.FOLIO_BASE_URL + '/item-storage/items?query=%s' % q
            response = requests.get(url, headers=headers, timeout=TIMEOUT)
            return json.loads(response.content)['items'][0]
        except (
            requests.exceptions.Timeout, json.decoder.JSONDecodeError,
            requests.exceptions.ConnectionError, IndexError, KeyError
        ):
            pass
    return dict()


def get_location(loc_id, token):
    """
    Queries the Folio location enpoint to get location information
    by ID.

    Args:
        loc_id: string

        token: string
    Returns:
        dict
    """
    headers = GENERIC_HEADERS
    headers.update({'X-Okapi-Token': token})
    try:
        response = requests.get(
            settings.FOLIO_BASE_URL + '/locations/%s' % loc_id,
            headers=headers,
            timeout=TIMEOUT
        )
        return json.loads(response.content)
    except (
        requests.exceptions.Timeout, json.decoder.JSONDecodeError,
        requests.exceptions.ConnectionError
    ):
        return dict()
