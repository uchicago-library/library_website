from base.models import PublicBasePage
from django.db import models
from wagtail.wagtailcore.models import Page
from xml.etree import ElementTree

import urllib

# Create your models here.
class FindingAidsPage(PublicBasePage):
    content_panels = Page.content_panels + PublicBasePage.content_panels

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

        def get_topics():
            topics = {}

            r = urllib.request.urlopen("http://marklogic.lib.uchicago.edu:8011/ead/topics.xqy")
            xml_string = "<body>" + str(r.read()) + "</body>"

            e = ElementTree.fromstring(xml_string)
            for div in e.findall('div'):
                subject = div.find('subject').text
                if not subject in topics:
                    topics[subject] = []
                topics[subject].append([div.find('eadid').text, div.find('title').text, div.find('abstract').find('abstract').text])

            return topics

        def get_topic_list(topics):
            topic_list = []
            for t in topics.keys():
                topic_list.append([t, len(topics[t])])
            return sorted(topic_list, key=lambda t: t[0])

        context = super(FindingAidsPage, self).get_context(request)

        searchq = request.GET.get('searchq', None)
        exactphrase = request.GET.get('exactphrase', None)
        topics = request.GET.get('topics', None)
        if topics and not topics == 'all':
            topics = None
        topic = request.GET.get('topic', None)
        digitized = request.GET.get('digitized', None)
        browse = request.GET.get('browse', None)

        # browse
        browses = get_browses()
        browselinks = get_browse_links(browses)
        if browse:
            browses = get_browse_list(browses, browse)

        all_topics = get_topics()

        # digitized
        digitizedlist = []
        if digitized:
            digitizedlist = get_digitized_content()

        # topics
        topiclist = []
        if topics:
            topiclist = get_topic_list(all_topics)

        # topic
        thistopiclist = []
        if topic:
            thistopiclist = list(sorted(all_topics[topic], key=lambda t: t[1]))

        # foreach /html/body/div
        # for d in e.findall('div'):
        # get the first span and second span- that's the EADID and title. 
            
        context['browse'] = browse
        context['browselinks'] = browselinks
        context['browses'] = browses
        context['digitized'] = digitized
        context['digitizedlist'] = digitizedlist
        context['exactphrase'] = exactphrase
        context['searchq'] = searchq
        context['topiclist'] = topiclist
        context['thistopiclist'] = thistopiclist
        context['topics'] = topics
        context['topic'] = topic

        return context
