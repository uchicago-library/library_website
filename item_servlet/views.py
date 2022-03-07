from django.http import JsonResponse
from library_website.settings import (
    FOLIO_TYPE_ISBN_ID, FOLIO_TYPE_ISSN_ID, FOLIO_TYPE_LINKING_ISSN_ID
)

from .utils import (
    get_auth, get_instances, get_item, get_location
)

# Lookup for identifier types
FOLIO_TYPE_IDS = {
    FOLIO_TYPE_ISBN_ID: 'isbn',
    FOLIO_TYPE_ISSN_ID: 'issn',
    FOLIO_TYPE_LINKING_ISSN_ID: 'linking_issn'
}


def parse_data(instances, item, location, bib=None, barcode=None):
    """
    Format data from Folio APIs into a simple dictionary that can be easily
    converted to JSON and plugged into a website.

    Args:
        instances: dict

        item: dict

        location: dict

        bib: string or None

        barcode: string or None

    Returns:
        dict
    """
    data = {
        'title': instances.get('title', ''),
        'location': location.get('discoveryDisplayName', ''),
        'internalLocation': location.get('name', ''),
        'callNumber': '',
        'callNumberPrefix': '',
        'copyNumber': '',
        'volumeNumber': '',
        'author': '',
        'bibId': '',
        'barcode': '',
        'publisher': '',
        'placePublished': '',
        'dateIssued': '',
        'edition': '',
        'issn': [],
        'isbn': [],
        'linking_issn': []
    }
    sep = ', '
    contributors = instances.get('contributors')
    publishers = instances.get('publication')
    publication_range = instances.get('publicationRange')
    editions = instances.get('editions')
    identifiers = instances.get('identifiers')
    if bib:
        data['bibId'] = bib
    if contributors:
        data['author'] = sep.join(a.get('name', '') for a in contributors)
    if publishers:
        data['publisher'] = sep.join(p.get('publisher', '') for p in publishers)
        data['placePublished'] = sep.join(
            p.get('place', '') for p in publishers
        )
    if publication_range:
        data['dateIssued'] = sep.join(d for d in publication_range)
    if editions:
        data['edition'] = sep.join(e for e in editions)
    if barcode and item:
        data['barcode'] = barcode
        callnum = item.get('effectiveCallNumberComponents')
        if callnum:
            data['callNumber'] = callnum.get('callNumber', '')
            data['callNumberPrefix'] = callnum.get('prefix', '')
        data['copyNumber'] = item.get('copyNumber', '')
        data['volumeNumber'] = item.get('enumeration', '')
    if identifiers:
        for i in identifiers:
            itype = FOLIO_TYPE_IDS.get(i.get('identifierTypeId'))
            ival = i.get('value')
            if itype == 'isbn' and ival:
                data['isbn'].append(ival)
            if itype == 'issn' and ival:
                data['issn'].append(ival)
            if itype == 'linking_issn' and ival:
                data['linking_issn'].append(ival)
    return data


def item_servlet(request):
    """
    View for retreiving bib and item information
    from the catalog.

    Args:
        request: object

    Returns:
        JsonResponse
    """
    if request.method == 'GET':
        bib = request.GET.get('bib', None)
        barcode = request.GET.get('barcode', None)
        auth = get_auth()
        token = auth['x-okapi-token']
        instances = get_instances(bib, token)
        item = get_item(barcode, token)
        location_id = item.get('effectiveLocationId')
        location = dict()
        if location_id:
            location = get_location(location_id, token)
        return JsonResponse(
            parse_data(instances, item, location, bib, barcode),
        )
