from datetime import datetime
from http.client import HTTPConnection
from xml.etree import ElementTree

import re

def get_xml_from_university_event_calendar():
    c = HTTPConnection('moss.lib.uchicago.edu', 8888)
    c.request('GET', '/tt-rss/public.php?op=rss&id=-4&key=4w4en5576c2601893f9')
    result = c.getresponse()
    xml_string = result.read()
    return ElementTree.fromstring(xml_string)

def get_flat_entries(x):
    entries = []
    for entry in x.findall('{http://www.w3.org/2005/Atom}entry'):
        content = entry.find('{http://www.w3.org/2005/Atom}content').text

        # date
        m = re.search('<strong>Date:</strong>([^<]*)<br>', content)
        try:
            date = m.group(1).strip()
        except:
            date = ''

        # starts
        m = re.search('<strong>Starts:</strong>([^<]*)<br>', content)
        try:
            starts = m.group(1).strip()
        except:
            starts = ''

        # ends
        m = re.search('<strong>Ends:</strong>([^<]*)<br>', content)
        try:
            ends = m.group(1).strip()
        except:
            ends = ''

        # date fallback...
        if date == '':
            date = starts

        # time
        m = re.search('<strong>Time:</strong>([^<]*)<br>', content)
        try:
            time = m.group(1).strip()
        except:
            time = ''

        # sortable date string: e.g. "2016-06-24 15:00"
        sortable_datetime = ''
        if date:
            s = date
        else:
            s = start
    
        sortable_datetime = datetime.strptime(s, '%B %d, %Y').strftime("%Y-%m-%d")

        date_label = datetime.strptime(s, '%B %d, %Y').strftime('%B %d, %Y').replace(' 0', ' ')

        if time == 'All Day':
            sortable_datetime = sortable_datetime + ' 00:00'
        else:
            sortable_datetime = sortable_datetime + datetime.strptime(time.split('-')[0].strip(), '%I:%M %p').strftime(" %H:%M")

        sortable_date = sortable_datetime.split(' ')[0]

        if date:
            time_label = time
        else:
            time_label = starts + ' - ' + ends

        # the date and time appear in the title, like "Aug 18: ", or "Aug 18, 5:00PM: ".
        # strip that out.
        title = re.sub(r'^.*?: ', '', entry.find('{http://www.w3.org/2005/Atom}title').text)

        # process content some more. 
        content = content.replace('<![CDATA[', '')
        # relace <br><br> and everything after with whitespace.
        content = re.sub(r'<br><br>.*$', '', content)

        entries.append({
            'content':           content,
            'date':              date,
            'date_label':        date_label,
            'link':              entry.find('{http://www.w3.org/2005/Atom}link').get('href'),
            'sortable_date':     sortable_date,
            'sortable_datetime': sortable_datetime,
            'summary':           entry.find('{http://www.w3.org/2005/Atom}summary').text,
            'time':              time,
            'time_label':        time_label,
            'title':             title
        })
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

        

