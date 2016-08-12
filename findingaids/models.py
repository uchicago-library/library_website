from base.models import PublicBasePage
from django.db import models
from wagtail.wagtailcore.models import Page
from xml.etree import ElementTree

import re
import urllib

class FindingAidsPage(PublicBasePage):
    content_panels = Page.content_panels + PublicBasePage.content_panels

    subpage_types = []

    def get_context(self, request):
        def get_browses():
            browses = []
    
            r = urllib.request.urlopen("http://marklogic.lib.uchicago.edu:8011/admin/gimme.xqy?collection=institution%2FUniversity%20of%20Chicago")
            xml_string = r.read()

            e = ElementTree.fromstring(xml_string)
            for div in e.find('body').findall('div'):
                span = div.findall('span')
                browses.append([span[0].text, span[1].text])
    
            return browses

        def get_browse_list(browses, browse):
            return sorted(list(filter(lambda b: b[1][0] == browse, browses)), key=lambda b: b[1])

        # e.g. "A", "B", "C"...
        def get_browse_links(browses):
            return sorted(list(set(map(lambda b: b[1][0], browses))))

        def get_digitized_content():
            digitized = []
        
            r = urllib.request.urlopen("http://marklogic:8011/admin/gimmeDigitalEADIDs.xqy")

            xml_string = r.read()

            e = ElementTree.fromstring(xml_string)
            for div in e.find('body').findall('div'):
                span = div.findall('span')
                digitized.append([span[0].find('eadid').text, span[1].text, span[2].find('abstract').text])

            return digitized

        def get_search_results(searchq):
            searchresults = []

            # If the search query came in starting and ending with double quotes, remove them
            # and process the search as an exact phrase query.
            exactphrase = False
            r = re.match(r'/^"(.*)"$/', searchq)
            if r:
                searchq = r.group(1)
                exactphrase = True

            if exactphrase:
                u = "http://marklogic.lib.uchicago.edu:8011/request.xqy?" + \
                urllib.parse.urlencode({'action': 'search', 'collection': 'project/SCRC', 'q': '"' + searchq + '"'})
            else:
                u = "http://marklogic.lib.uchicago.edu:8011/request.xqy?" + \
                urllib.parse.urlencode({'action': 'search', 'collection': 'project/SCRC', 'q': searchq})

            r = urllib.request.urlopen(u)

            xml_string = r.read()

            e = ElementTree.fromstring(xml_string)
            try:
                for div in e.find("div[@class='search-results']").findall("div[@class='search-result']"):
                    searchresults.append({
                        'eadid': div.find("div[@class='eadid']").text,
                        'title': div.find("div[@class='project']").text,
                        'abstract': div.find("div[@class='abstract']").text
                    })
            except AttributeError:
                pass

            return searchresults

        def get_topics():
            topics = {}

            r = urllib.request.urlopen("http://marklogic.lib.uchicago.edu:8011/ead/topics.xqy")
            xml_string = "<body>" + str(r.read()) + "</body>"

            e = ElementTree.fromstring(xml_string)
            for div in e.findall('div'):
                subject = div.find('subject').text

                if not subject:
                    continue

                if not subject in topics:
                    topics[subject] = []

                topic_data = {}
                for f in ['eadid', 'title']:
                    try:
                        topic_data[f] = div.find(f).text
                    except:
                        topic_data[f] = ''

                try:
                    topic_data['abstract'] = div.find('abstract').find('abstract').text
                except:
                    topic_data['abstract'] = ''
                    
                topics[subject].append([topic_data['eadid'], topic_data['title'], topic_data['abstract']])

            return topics

        def get_topic_list(topics):
            topic_list = []
            for t in topics.keys():
                topic_list.append([t, len(topics[t])])
            return sorted(topic_list, key=lambda t: t[0])

        context = super(FindingAidsPage, self).get_context(request)

        browse = request.GET.get('browse', None)
        digitized = request.GET.get('digitized', None)
        searchq = request.GET.get('searchq', None)
        topic = request.GET.get('topic', None)
        topics = request.GET.get('topics', None)
        if topics and not topics == 'all':
            topics = None
        view = request.GET.get('view', None)
        if not view:
            view = 'title'

        # browse
        browses = get_browses()
        browselinks = get_browse_links(browses)
        if browse:
            browses = get_browse_list(browses, browse)

        all_topics = get_topics()

        # digitized
        digitizedlist = []
        if view == 'digitized':
            digitizedlist = get_digitized_content()

        # search
        searchresults = []
        searchresultcount = 0
        if searchq:
            searchresults = get_search_results(searchq)
            searchresultcount = len(searchresults)

        # topics
        topiclist = []
        if view == 'topics':
            topiclist = get_topic_list(all_topics)

        # topic
        thistopiclist = []
        if topic:
            thistopiclist = list(sorted(all_topics[topic], key=lambda t: t[1]))

        context['browse'] = browse
        context['browselinks'] = browselinks
        context['browses'] = browses
        context['digitized'] = digitized
        context['digitizedlist'] = digitizedlist
        context['searchq'] = searchq
        context['searchresultcount'] = searchresultcount
        context['searchresults'] = searchresults
        context['topiclist'] = topiclist
        context['thistopiclist'] = thistopiclist
        context['topics'] = topics
        context['topic'] = topic
        context['view'] = view

        return context
