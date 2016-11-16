from datetime import datetime
from http.client import HTTPConnection
from urllib.parse import parse_qs, urlparse
from xml.etree import ElementTree

import re

def get_xml_from_feed(feed):
    p = urlparse(feed)

    if p.scheme != 'http':
        raise ValueError

    # p.netloc is "www3.lib.uchicago.edu"
    c = HTTPConnection(p.netloc, 80)

    c.request('GET', p.path + "?" + p.query)
    result = c.getresponse()
    xml_string = result.read()
    return ElementTree.fromstring(xml_string)

def get_entries_from_events_uchicago(x):
    entries = {}
    for entry in x.find('channel').findall('item'):
        entries[entry.find('guid').text] = {
            'start_date': entry.find('startDate').text,
            'start_time': entry.find('startTime').text,
            'end_date': entry.find('endDate').text,
            'end_time': entry.find('endTime').text
        }
    return entries

# 
# input: xml from university event feed.
#
def get_flat_entries_from_ttrss(x):
    entries = []
    for entry in x.findall('{http://www.w3.org/2005/Atom}entry'):
        content = entry.find('{http://www.w3.org/2005/Atom}content').text

        # the date and time appear in the title, like "Aug 18: ", or "Aug 18, 5:00PM: ".
        # strip that out.
        title = re.sub(r'^.*?: ', '', entry.find('{http://www.w3.org/2005/Atom}title').text)

        # process content some more. 
        content = content.replace('<![CDATA[', '')
        # relace <br><br> and everything after with whitespace.
        content = re.sub(r'<br><br>.*$', '', content)

        link = entry.find('{http://www.w3.org/2005/Atom}link').get('href')
        query = urlparse(link).query
        guid = parse_qs(query)['guid'][0]

        entries.append({
            'content':           content,
            'guid':              guid,
            'link':              link,
            'summary':           entry.find('{http://www.w3.org/2005/Atom}summary').text,
            'title':             title
        })
    return entries

# collect all entries into a list of lists. 
# [ 
#   [ '20160623', [ list-of-entries ] ],
#   ...
# ]
def group_ttrss_entries(entries):
    entries_out = []
    for entry in entries:
        # find the entry index for this sortable_date.
        i = 0
        while i < len(entries_out):
            if entries_out[i][0] == entry['sortable_date']:
                break
            i = i + 1
        # add a new date if necessary.
        if i == len(entries_out):
            entries_out.append([entry['sortable_date'], []])
        # append this entry to that slot. 
        entries_out[i][1].append(entry)

    # sort entries
    entries_out = sorted(entries_out, key=lambda e: e[0])
    i = 0
    while i < len(entries_out):
        entries_out[i][1] = sorted(entries_out[i][1], key=lambda e: e['sortable_datetime'])
        i = i + 1

    return entries_out

def add_university_fields_to_ttrss_entries(university_entries, ttrss_entries):
    """
    Combine data from the University events calendar feed with the
    Library's Tiny Tiny RSS feed and return a new data structure
    with all the fields.

    Args:
        university_entries: dictionary of fields parsed from the
        University events xml feed.

        ttrss_entries: list of dictionaries of fields parsed from
        the Tiny Tiny RSS feed.

    Returns:
        A list of dictionaries with combined data about events.
        The new datastructure combines fields from the University
        xml feed and the Tiny Tiny Rss feed.
    """
    i = 0
    while i < len(ttrss_entries):
        guid = ttrss_entries[i]['guid']
        date = university_entries[guid]['start_date']
        time = university_entries[guid]['start_time']
        sortable_date = datetime.strptime(date, '%B %d, %Y').strftime("%Y-%m-%d")
        sortable_datetime = sortable_date + ' ' + datetime.strptime(time, '%I:%M %p').strftime('%H:%M')
        ttrss_entries[i]['date'] = date
        ttrss_entries[i]['date_label'] = date
        ttrss_entries[i]['time'] = time
        ttrss_entries[i]['time_label'] = time
        ttrss_entries[i]['sortable_date'] = sortable_date
        ttrss_entries[i]['sortable_datetime'] = sortable_datetime
        i = i + 1
    return ttrss_entries

def get_events(university_xml, ttrss_xml, start, stop):
    """
    Return a datastructure containing events data parsed from
    the University events feed and Tiny Tiny Rss.

    Args:
        university_xml: ElementTree xml object representing
        xml from the university calendar feed.

        ttrss_xml: ElementTree xml object representing xml
        from the Tiny Tiny RSS feed.

        start: datetime object.

        stop: datetime object.

    Returns:
        A list of lists where the first item of each list
        is a date string and the second item is a list
        containing dictionaries. Dictionary keys include
        time_label, guid, date_label, date, content, link,
        sortable_date, title, and time.
    """
    # get xml from the university event feed directly. 
    university_entries = get_entries_from_events_uchicago(university_xml)

    # get info from the event calendar as a list of lists.
    ttrss_entries = get_flat_entries_from_ttrss(ttrss_xml)

    # add fields. 
    ttrss_entries = add_university_fields_to_ttrss_entries(university_entries, ttrss_entries)

    # group entries. 
    ttrss_entries = group_ttrss_entries(ttrss_entries)

    # only pass along the entries that make sense for this date range. 
    entries_out = []
    i = 0
    while i < len(ttrss_entries):
        if ttrss_entries[i][0] >= start.strftime('%Y-%m-%d') and ttrss_entries[i][0] <= stop.strftime('%Y-%m-%d'):
            entries_out.append(ttrss_entries[i])
        i = i + 1

    return entries_out
