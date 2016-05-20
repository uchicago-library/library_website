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

        def get_topics():
            topics = []

            r = urllib.request.urlopen("http://marklogic.lib.uchicago.edu:8011/ead/topics.xqy")
            xml_string = "<body>" + r.read() + "</body>"

            e = ElementTree.fromstring(xml_string)
            for div in e.findall('div'):
                subject = div.find('subject')
                topics.append(subject)

            return topics

        context = super(FindingAidsPage, self).get_context(request)

        searchq = request.GET.get('searchq', None)
        exactphrase = request.GET.get('exactphrase', None)
        topics = request.GET.get('topics', None)
        topic = request.GET.get('topic', None)
        digitized = request.GET.get('digitized', None)
        browse = request.GET.get('browse', None)

        # browse
        browses = get_browses()
        browselinks = get_browse_links(browses)
        if browse:
            browses = get_browse_list(browses, browse)

        # topics
        if topics:
            topiclist = get_topics()

        # foreach /html/body/div
        # for d in e.findall('div'):
        # get the first span and second span- that's the EADID and title. 
            
        context['searchq'] = searchq
        context['exactphrase'] = exactphrase
        context['topiclist'] = topiclist
        context['topics'] = topics
        context['topic'] = topic
        context['digitized'] = digitized
        context['browse'] = browse
        context['browselinks'] = browselinks
        context['browses'] = browses

        return context
