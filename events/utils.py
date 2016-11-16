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
    entries = []
    for entry in x.find('channel').findall('item'):
        content = entry.find('description').text
        # remove CDATA marker. 
        content = content.replace('<![CDATA[', '')
        # remove line breaks.
        content = re.sub(r'<br><br>.*$', '', content)

        guid = entry.find('guid').text

        start_date = entry.find('startDate').text
        start_time = entry.find('startTime').text
    
        sortable_date = datetime.strptime(start_date, '%B %d, %Y').strftime('%Y-%m-%d')
        sortable_datetime = sortable_date + ' ' + datetime.strptime(start_time, '%I:%M %p').strftime('%H:%M')
        
        # the date and time appear in the title, like "Aug 18: ", or "Aug 18, 5:00PM: ".
        # strip that out.
        title = re.sub(r'^.*?: ', '', entry.find('title').text)

        entries.append({
            'content': content,
            'date_label': start_date,
            'end_date': entry.find('endDate').text,
            'end_time': entry.find('endTime').text,
            'guid': guid,
            'link': entry.find('link').text,
            'sortable_date': sortable_date,
            'sortable_datetime': sortable_datetime,
            'start_date': start_date,
            'start_time': start_time,
            'summary': content,
            'time': start_time,
            'time_label': start_time,
            'title': title
        })
    return entries

# 
# input: xml from university event feed.
#
def get_flat_entries_from_ttrss(x):
    entries = []
    for entry in x.findall('{http://www.w3.org/2005/Atom}entry'):
        #category = entry.find('{http://www.w3.org/2005/Atom}category').get('term')
        link = entry.find('{http://www.w3.org/2005/Atom}link').get('href')
        query = urlparse(link).query
        guid = parse_qs(query)['guid'][0]
        entries.append({'guid': guid})
    return entries

# collect all entries into a list of lists. 
# [ 
#   [ '20160623', [ list-of-entries ] ],
#   ...
# ]
def group_entries(entries):
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

def filter_university_entries_to_ttrss_entries(university_entries, ttrss_entries):
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
    ttrss_guids = []
    for ttrss_entry in ttrss_entries:
        ttrss_guids.append(ttrss_entry['guid'])

    entries_out = []
    for entry in university_entries:
        if entry['guid'] in ttrss_guids:
            entries_out.append(entry)
    return entries_out

def get_events(university_url, ttrss_url, start, stop, full_view = True):
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
    ttrss_xml = get_xml_from_feed(ttrss_url)
    university_xml = get_xml_from_feed(university_url)

    query = urlparse(ttrss_url).query
    category = parse_qs(query)['id'][0]

    # get xml from the university event feed directly. 
    university_entries = get_entries_from_events_uchicago(university_xml)

    # get info from the event calendar as a list of lists.
    ttrss_entries = get_flat_entries_from_ttrss(ttrss_xml)

    # filter to TTRSS entries only.
    if not full_view:
        university_entries = filter_university_entries_to_ttrss_entries(university_entries, ttrss_entries)

    # group entries. 
    grouped_entries = group_entries(university_entries)

    # only pass along the entries that make sense for this date range. 
    entries_out = []
    i = 0
    while i < len(grouped_entries):
        if grouped_entries[i][0] >= start.strftime('%Y-%m-%d') and grouped_entries[i][0] <= stop.strftime('%Y-%m-%d'):
            entries_out.append(grouped_entries[i])
        i = i + 1

    return entries_out
