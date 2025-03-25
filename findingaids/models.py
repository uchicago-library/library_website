from base.models import PublicBasePage
from library_website.settings import MARKLOGIC_LDR_BASE, MARKLOGIC_FINDINGAIDS_PORT
from wagtail.models import Page
from xml.etree import ElementTree
from django.core.paginator import Paginator
from django.core.cache import cache

import re
import urllib
import json

class FindingAidsPage(PublicBasePage):
    content_panels = Page.content_panels + PublicBasePage.content_panels

    subpage_types = []

    def get_context(self, request):
        def marklogic_url(route):
            return "%s:%i%s" % (
                MARKLOGIC_LDR_BASE,
                MARKLOGIC_FINDINGAIDS_PORT,
                route,
            )

        def get_marklogic_xml(route):
            try:
                r = urllib.request.urlopen(
                    marklogic_url(route)
                )
                xml_string = r.read().decode('utf-8')
                return xml_string
            except urllib.error.URLError:
                return ''

        def get_browses():
            browses = []

            route = ('/admin/gimme.xqy'
                     '?collection=institution%2FUniversity%20of%20Chicago')

            xml_string = get_marklogic_xml(route)

            try:
                e = ElementTree.fromstring(xml_string)
                for div in e.find('body').findall('div'):
                    span = div.findall('span')
                    if span[0].text and span[1].text:
                        browses.append([span[0].text, span[1].text])
                    else:
                        pass
            except ElementTree.ParseError:
                pass

            return browses

        def get_browse_list(browses, browse):
            return sorted(
                list(filter(
                    lambda b: b[1][0] == browse, browses
                )),
                key=lambda b: b[1]
            )

        # e.g. "A", "B", "C"...
        def get_browse_links(browses):
            return sorted(list(set(map(lambda b: b[1][0], browses))))

        def get_digitized_content():

            digitized = []

            route = '/admin/gimmeDigitalEADIDs.xqy'

            xml_string = get_marklogic_xml(route)

            try:
                e = ElementTree.fromstring(xml_string)
                for div in e.find('body').findall('div'):
                    span = div.findall('span')
                    digitized.append([span[0].find('eadid').text,
                                      span[1].text, span[2].find(
                                          'abstract').text]
                                     )
            except ElementTree.ParseError:
                pass

            return digitized

        def get_search_results(searchq):
            searchresults = []

            # If the search query came in starting and ending with
            # double quotes, remove them and process the search as an
            # exact phrase query.
            exactphrase = False
            r = re.match(r'/^"(.*)"$/', searchq)
            if r:
                searchq = r.group(1)
                exactphrase = True

            if exactphrase:
                route = "/request.xqy?" + urllib.parse.urlencode(
                        {'action': 'search', 'collection': 'project/SCRC',
                            'q': '"' + searchq + '"'}
                )
            else:
                route = "/request.xqy?" + urllib.parse.urlencode(
                        {'action':
                         'search',
                         'collection':
                         'project/SCRC',
                         'q': searchq
                         }
                )

            xml_string = get_marklogic_xml(route)

            try:
                e = ElementTree.fromstring(xml_string)
                for div in e.find(
                        "div[@class='search-results']"
                ).findall("div[@class='search-result']"):
                    searchresults.append({
                        'eadid': div.find("div[@class='eadid']").text,
                        'title': div.find("div[@class='project']").text,
                        'abstract': div.find("div[@class='abstract']").text
                    })
            except (AttributeError, ElementTree.ParseError):
                pass

            return searchresults

        def get_topics():
            topics = {}

            route = "/ead/topics.xqy"

            xml_string = "<body>" + get_marklogic_xml(route) + "</body>"

            try:
                e = ElementTree.fromstring(xml_string)
                for div in e.findall('div'):
                    subject = div.find('subject').text

                    if subject is None:
                        continue

                    if subject not in topics:
                        topics[subject] = []

                    topic_data = {}
                    for f in ['eadid', 'title']:
                        try:
                            topic_data[f] = div.find(f).text
                        except AttributeError:
                            topic_data[f] = ''

                    try:
                        topic_data['abstract'] = div.find(
                            'abstract').find('abstract').text
                    except AttributeError:
                        topic_data['abstract'] = ''

                    topics[subject].append(
                        [topic_data['eadid'],
                         topic_data['title'],
                         topic_data['abstract']])
            except ElementTree.ParseError:
                pass

            return topics

        def get_topic_list(topics):
            topic_list = []
            for t in topics.keys():
                topic_list.append([t, len(topics[t])])
            return sorted(topic_list, key=lambda t: t[0])

        context = super(FindingAidsPage, self).get_context(request)

        browse = request.GET.get('browse', 'all')
        digitized = request.GET.get('digitized', None)
        searchq = request.GET.get('searchq', None)
        topic = request.GET.get('topic', None)
        topics = request.GET.get('topics', None)
        if topics and not topics == 'all':
            topics = None
        view = request.GET.get('view', 'title')

        # search
        searchresults = []
        searchresultcount = 0
        if searchq:
            searchresults = get_search_results(searchq)
            searchresultcount = len(searchresults)

        cached_browses = cache.get("finding_aids_all_browses")

        if cached_browses:
            all_browses = json.loads(cached_browses)
        else:
            all_browses = get_browses()
            cache.set("finding_aids_all_browses", json.dumps(all_browses))
        
        paginator = Paginator(all_browses, 100)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        num_pages = paginator.num_pages

        if browse != 'all':
            browses = get_browse_list(all_browses, browse)
            browselinks = get_browse_links(all_browses)
        else:
            browses = None
            browselinks = get_browse_links(all_browses)

        all_topics = get_topics()

        digitizedlist = []
        topiclist = []
        thistopiclist = []

        if view == 'digitized':
            digitizedlist = get_digitized_content()
        elif view == 'topics':
            topiclist = get_topic_list(all_topics)
            if topic:
                try:
                    thistopiclist = list(
                        sorted(all_topics[topic], key=lambda t: t[1]))
                except KeyError:
                    thistopiclist = []

        context["page_obj"] = page_obj
        context["num_pages"] = num_pages
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
