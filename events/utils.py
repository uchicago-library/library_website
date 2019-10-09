from datetime import datetime, timedelta
from http.client import HTTPConnection, HTTPSConnection
from urllib.parse import parse_qs, urlparse
from xml.etree import ElementTree

import itertools
import re

def get_xml_from_feed(feed):
    p = urlparse(feed)

    # p.netloc is "www3.lib.uchicago.edu"
    if p.scheme == 'https':
        c = HTTPSConnection(p.netloc, 443)
    else:
        c = HTTPConnection(p.netloc, 80)

    c.request('GET', p.path + "?" + p.query)
    result = c.getresponse()
    xml_bytes = result.read()
    return ElementTree.fromstring(xml_bytes.decode('utf-8'))

def get_entries_from_events_uchicago(x):
    entries = []
    for entry in x.find('channel').findall('item'):
        content = truncate_summary(entry.find('description').text)

        guid = entry.find('guid').text

        start_date = entry.find('startDate').text
        start_time = entry.find('startTime').text

        end_date = entry.find('endDate').text
        end_time = entry.find('endTime').text
    
        sortable_date = datetime.strptime(start_date, '%B %d, %Y').strftime('%Y-%m-%d')
        sortable_datetime = sortable_date + ' ' + datetime.strptime(start_time, '%I:%M %p').strftime('%H:%M')

        sortable_end_date = datetime.strptime(end_date, '%B %d, %Y').strftime('%Y-%m-%d')

        start_date_short_form = datetime.strptime(start_date, '%B %d, %Y').strftime('%m/%d')
        end_date_short_form = datetime.strptime(end_date, '%B %d, %Y').strftime('%m/%d')
        
        # the date and time appear in the title, like "Aug 18: ", or "Aug 18, 5:00PM: ".
        # strip that out.
        title = re.sub(r'^.*?: ', '', entry.find('title').text)

        entries.append({
            'content': content,
            'end_date': end_date,
            'end_date_short_form': end_date_short_form,
            'end_time': end_time,
            'guid': guid,
            'link': entry.find('link').text,
            'sortable_date': sortable_date,
            'sortable_date_label': start_date,
            'sortable_datetime': sortable_datetime,
            'sortable_end_date': sortable_end_date,
            'start_date': start_date,
            'start_date_short_form': start_date_short_form,
            'start_time': start_time,
            'summary': content,
            'title': title
        })
    return entries

def expand_multiday_entries(entries, nudge_to_date):
    """
    On the workshops and events widget, multiday events should be
    "nudged" to appear on the current day. On the full events 
    view, multiday events should appear once on each day they
    span. 

    Args:
        entries: dictionary of fields parsed from the
        University events xml feed.

        nudge_to_date: for display on the workshops and events 
        widget, this is the day that multiday events should be 
        "nudged" to. This will probably be today's date, except for 
        testing. For a full listing of all dates, pass "none". 

    Returns:
        A list of dictionaries with multiday events either repeated
        or nudged up to the current day. 
    """
    entries_out = []
    i = 0 
    while i < len(entries):
        if entries[i]['start_date'] == entries[i]['end_date']:
            entries_out.append(entries[i])
        else:
            start_date = datetime.strptime(entries[i]['start_date'], '%B %d, %Y')
            current_date = start_date
            end_date = datetime.strptime(entries[i]['end_date'], '%B %d, %Y')
            while current_date <= end_date:
                if nudge_to_date == None or current_date.date() == nudge_to_date:
                    # using dict() makes a new copy. 
                    tmp = dict(entries[i])
                    tmp['sortable_date'] = current_date.strftime('%Y-%m-%d')
                    tmp['sortable_date_label'] = current_date.strftime('%B %d, %Y')
                    tmp['sortable_datetime'] = current_date.strftime('%Y-%m-%d')
                    entries_out.append(tmp)
                    if nudge_to_date != None:
                        current_date = end_date
                current_date = current_date + timedelta(days=1)
        i = i + 1
    return entries_out

# 
# input: xml from university event feed.
#
def get_flat_entries_from_ttrss(x):
    entries = []
    for entry in x.findall('{http://www.w3.org/2005/Atom}entry'):
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

def truncate_summary(summary_string):
    # remove CDATA marker. 
    summary_string = summary_string.replace('<![CDATA[', '')

    # remove dates, times, hyperlinks, etc. 
    summary_string = re.sub(r'<strong>Date:</strong>[^<]*<br />', '', summary_string)
    summary_string = re.sub(r'<strong>Ends:</strong>[^<]*<br />', '', summary_string)
    summary_string = re.sub(r'<strong>See:</strong>\s*<a[^<]*</a><br />', '', summary_string)
    summary_string = re.sub(r'<strong>Starts:</strong>[^<]*<br />', '', summary_string)
    summary_string = re.sub(r'<strong>Time:</strong>[^<]*<br />', '', summary_string)

    # remove nulls and characters that don't fit into seven bits. 
    summary_string = re.sub('[\0\200-\377]', '', summary_string)

    # remove HTML tags. 
    summary_string = re.sub('<.*?>', '', summary_string)
    
    # replace all whitespace with a single space. 
    summary_string = re.sub('\s+', ' ', summary_string)

    # string should be no more than 140 characters long, 
    # split on a word boundary. 
    character_count = 0
    needs_ellipses = False
    words_out = []
    for word in summary_string.split():
        character_count = character_count + 1 + len(word)
        if character_count > 140:
            needs_ellipses = True
            break
        words_out.append(word)

    summary_string = ' '.join(words_out)
    if needs_ellipses:
        summary_string = summary_string + '...'

    return summary_string

def get_events(university_url, ttrss_url, start, stop, full_view = True):
    """
    Return a datastructure containing events data parsed from
    the University events feed and Tiny Tiny Rss.

    Args:
        university_xml: ElementTree xml object representing
        xml from the university calendar feed. e.g.:
        http://events.uchicago.edu/widgets/rss.php?key=47866f880d62a4f4517a44381f4a990d&id=48

        ttrss_xml: ElementTree xml object representing xml
        from the Tiny Tiny RSS feed. e.g.
        http://www3.lib.uchicago.edu/tt-rss/public.php?op=rss&id=-3&key=8idjnk57e2a0063541d

        start: datetime object, or None.

        stop: datetime object, or None.

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
    entries = get_entries_from_events_uchicago(university_xml)

    # get info from the event calendar as a list of lists.
    ttrss_entries = get_flat_entries_from_ttrss(ttrss_xml)

    if not full_view:
        entries = expand_multiday_entries(entries, datetime.now().date())
        entries = filter_university_entries_to_ttrss_entries(entries, ttrss_entries)
    
    # group entries. 
    grouped_entries = group_entries(entries)

    # only pass along the entries that make sense for this date range. 
    entries_out = []
    #if start and stop:
    i = 0
    while i < len(grouped_entries):
        if start and stop:
            if grouped_entries[i][0] >= start.strftime('%Y-%m-%d') and grouped_entries[i][0] <= stop.strftime('%Y-%m-%d'):
                entries_out.append(grouped_entries[i])
        else:
            entries_out.append(grouped_entries[i])
        i = i + 1

    return entries_out

def flatten_events(events):
    """
    Takes the data structure from get_events and returns a "flattened" version
    of it, with just events, not grouped by leading dates.
    """
    return list(itertools.chain(*[event_data[1] for event_data in events]))







