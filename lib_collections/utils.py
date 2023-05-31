"""
iiifcollectionbrowse
"""

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import json
import re
import ipaddress
from urllib.parse import urlencode

import requests
from django.utils.text import slugify
from library_website.settings import (
    IIIF_PREFIX,
    IIIF_VIEWER_PREFIX,
    WAGTAIL_PREFIX,
    LANGUAGE_ABBREVS,
    CITATION_ROOT,
    TURTLE_ROOT
)
from base.result import Result


class GeneralPurpose():
    """
    Namespace class containing some general-purpose functions.  In the
    context of this module, they're here to help with unit testing.
    See tests.py.

    """

    def noop(x):
        """
        Noop function.

        Args:
            x: anything

        Returns:
            Side effect-ful; no return value
        """
        pass

    def identity(x):
        """
        The identity function.

        Args:
            x: anything

        Returns:
            The same thing.
        """
        return x

    def k(x):
        """
        Curry's K-combinator.  Returns a constant function to the input.

        Args:
            x: anything

        Returns:
            A constant function to the input.
        """
        def partial(y):
            return x
        return partial


class CBrowseURL():
    """
    Namespace class containing utility functions for creating cluster
    browse URLs for both Wagtail and IIIF
    """

    def mk_cbrowse_url(
        prefix: str, slug: str, browse_type: str, browse_name: str,
        extension: str
    ) -> str:
        """
        Create a local route to a digital collections cluster browse.

        Args:
            prefix: root url, string

            slug: name of collection slug, string

            browse_type: name of browse type, string

            browse_name: name of browse, string

            extension: filename extension, string

        Returns:
            URL string
        """
        return "%s/%s/cluster-browse/%s/%s%s" % (
            prefix, slug, browse_type, browse_name, extension
        )

    def mk_cbrowse_url_iiif(
        slug: str, browse_name: str, browse_type: str
    ) -> str:
        """
        mk_cbrowse_url, specialized to the IIIF host
        """
        return CBrowseURL.mk_cbrowse_url(
            IIIF_PREFIX, slug, browse_type, browse_name, ".json"
        )

    def mk_cbrowse_url_wagtail(
        slug: str,
        browse_type: str,
        browse_name: str,
        full: bool = False
    ) -> str:
        """
        mk_cbrowse_url, specialized to the Wagtail host

        full boolean input parameter determines whether it is a local
        or global URL

        Args:
            slug: name of collection slug, string

            browse_type: name of browse type, string

            browse_name: name of browse, string

            full: whether to build global URL, bool

        Returns:
            URL string
        """
        url = CBrowseURL.mk_cbrowse_url(
            WAGTAIL_PREFIX, slug, browse_type, browse_name, ""
        )
        if full:
            return "https://www.lib.uchicago.edu" + url
        else:
            return url

    def mk_cbrowse_type_url(
        prefix: str, slug: str, browse_type: str, extension: str
    ) -> str:
        """
        Create a local route to a digital collections cluster browse type.

        Args:
            prefix: root url, string

            slug: name of collection slug, string

            browse_type: name of browse type, string

            extension: filename extension, string

        Returns:
            URL string
        """
        return "%s/%s/cluster-browse/%s%s" % (
            prefix, slug, browse_type, extension
        )

    def mk_cbrowse_type_url_iiif(slug: str, browse_type: str) -> str:
        """
        mk_cbrowse_type_url, specialized to the IIIF host

        Args:
            slug: name of collection slug, string

            browse_type: name of browse type, string

        Returns:
            URL string
        """
        return CBrowseURL.mk_cbrowse_type_url(
            IIIF_PREFIX, slug, browse_type, ".json"
        )

    def mk_cbrowse_type_url_wagtail(
        slug: str, browse_type: str, full: bool = False
    ) -> str:
        """
        mk_cbrowse_type_url, specialized to the Wagtail host
        Args:
            slug: name of collection slug, string

            browse_type: name of browse type, string

        Returns:
            URL string
        """
        url = CBrowseURL.mk_cbrowse_type_url(
            WAGTAIL_PREFIX, slug, browse_type, ""
        )
        if full:
            return "https://www.lib.uchicago.edu" + url
        else:
            return url


class LBrowseURL():
    """
    Namespace class containing utility functions for creating list
    browse URLs for both Wagtail and IIIF
    """

    def mk_lbrowse_url(
        prefix: str, slug: str, browse_name: str, extension: str
    ) -> str:
        """
        Create a local route to a digital collections list browse.

        Args:
            prefix: root url, string

            slug: name of collection slug, string

            browse_name: name of browse, string

            extension: filename extension, string

        Returns:
            URL string
        """
        return "%s/%s/list-browse/%s%s" % (prefix,
                                           slug,
                                           browse_name,
                                           extension)

    def mk_lbrowse_url_iiif(slug: str, browse_name: str) -> str:
        """
        mk_lbrowse_url, specialized to the IIIF host

        Args:
            slug: name of collection slug, string

            browse_name: name of browse, string

        Returns:
            URL string
        """
        return LBrowseURL.mk_lbrowse_url(
            IIIF_PREFIX, slug, browse_name, ".json"
        )

    def mk_lbrowse_url_wagtail(slug: str, browse_name: str) -> str:
        """
        mk_lbrowse_url, specialized to the Wagtail host
        """
        return LBrowseURL.mk_lbrowse_url(WAGTAIL_PREFIX, slug, browse_name, "")


class DisplayBrowse():
    """
    Namespace class containing code for generating digital collection
    object listings, intermediate cluster browses, and object page
    links Wagtail

    """

    def unslugify_browse(slug: str) -> str:
        """
        Turn a browse slug back into the capitalized name of a browse for
        display in the page.

        Args:
            slug: name of browse in slug form, string

        Returns:
            string representing the name of the browse
        """
        slug_list = slug.split('-')
        spaces = ' '.join([x.capitalize() for x in slug_list])
        return spaces

    def get_iiif_labels_language(url: str,
                                 lang: str,
                                 modify=GeneralPurpose.noop) -> list:
        """
        Helper function for get_iiif_labels.

        Args:

            url: URL for IIIF browse listing, string

            lang: language abbreviation, e.g. 'en', string

            modify: response modifying-function for testing, function

        Returns:
            an association list from browses/browse types to the
            number of items falling under each browse

        """
        r = requests.get(url)
        modify(r)
        if r.status_code == 404:
            return []
        else:
            j = r.json()
            d = j['items']
            return [
                (x['label'][lang][0], x['metadata'][0]['value'][lang][0])
                for x in d
            ]

    def get_iiif_labels(url: str,
                        browse_type: str,
                        slug: str,
                        modify=GeneralPurpose.noop) -> dict:
        """
        Get IIIF data corresponding to a list of browses, package it up in
        JSON data for display in the Wagtail browse template
        (templates/collection_browse.html)

        Args:
            url: URL for IIIF browse listing, string

            browse_type: browse type, string

            modify: response modifying-function for testing, function

        Returns:
            JSON data for the browse list template
        """

        # turn association list into a dictionary
        def lists_to_dict(lst1: list, lst2: list) -> dict:
            return dict(zip(lst1, lst2))

        # assume English as the default language for now; the language
        # abbreviation can be parameterized later
        try:
            pairs = DisplayBrowse.get_iiif_labels_language(
                url, 'en', modify=modify)
        except requests.exceptions.RequestException:
            pairs = []

        def render_count(pairs: list) -> list:
            return ["%s (%s)" % (x, y) for (x, y) in pairs]

        labels = [x[0] for x in pairs]

        # output dictionary for display in browse template
        return lists_to_dict(
            render_count(pairs), [
                CBrowseURL.mk_cbrowse_url_wagtail(
                    slug, browse_type, slugify(label)
                ) for label in labels
            ]
        )

    def mk_wagtail_object_url(collection_slug: str, manifid: str) -> str:
        """
        Create Wagtail URL for collection object.


        Args:
            collection_slug: name of collection in slug form, string

            manifid: ARK NOID, string

        Returns:
            Wagtail URL for the object with the relevant NOID
        """
        return (
            "/collex/collections/%s/object/%s" %
            (collection_slug, manifid)
        )

    def create_field(name: str, dct: dict) -> list:
        """
        Helper function for prepare_browse_json.

        Args:
            name: metadata field name, string

            dct: IIIF json data, dictionary

        Returns:
            list of values for that field
        """
        if name in dct.keys():
            return dct[name]
        else:
            return []

    def iiif_field_update(dct: dict, field: str, val: str):
        """
        Helper function for prepare_browse_json.

        Args:
            dct: IIIF json data, dictionary

            field: metadata field, string

            value: metadata value, string

        Returns:
            n/a; side effect-ful function that mutates the input
            dictionary so as to contain the input key and value
        """
        if field in dct.keys():
            new_value = dct[field] + [val]
            dct.update({field: new_value})
        else:
            dct[field] = [val]

    def pull_metadata_labels(j: dict) -> dict:
        """
        Helper function for prepare_browse_json.

        Args:
            j: IIIF json data, dictionary

        Returns:
            dictionary with field strings as fields and lists of
            values as values
        """
        output: dict = {}
        for x in j['metadata']:
            DisplayBrowse.iiif_field_update(
                output,
                x['label']['en'][0].lower(),
                x['value']['en'][0],
            )
        return output

    def extract_manifid_thumbnail(url: str) -> str:
        """
        Pulls the NOID for a collection object out of the URL for its
        thumbnail by regular expression matching on the ARK ID.

        Args:
            url: url to IIIF thumbnail for object, string

        Returns:
            Collection object NOID

        """
        rexp = re.search(r'.*\/ark\%3A61001\%2F([\d|\w]+)/', url)
        try:
            return rexp[1]
        except TypeError:
            return ''

    def comma_join(lst):
        """
        Joins a list of strings by commas.  For use as the second input to
        prepare_browse_json.

        Args:
            lst: list of strings

        Returns:
            Comma-joined string
        """
        return ", ".join(lst)

    def prepare_browse_json(j: dict, joiner) -> dict:
        """
        Creates a JSON/dictionary representation of the data to be
        displayed for each item in a browse.

        Args:
            j: IIIF json data, dictionary

            joiner: string joining function

        Returns:
            dictionary with field strings as fields and lists of
            values as values; supplies the content for each listing of
            a collection item in each browse

        """
        manifid = DisplayBrowse.extract_manifid_thumbnail(
            j['thumbnail'][0]['id']
        )

        metadata = DisplayBrowse.pull_metadata_labels(j)
        create_field = DisplayBrowse.create_field

        title = create_field('title', metadata)
        publisher = create_field('publisher', metadata)
        creator = create_field('creator', metadata)
        date = create_field('date', metadata)
        language = create_field('language', metadata)

        output = {
            'title':
            joiner(title),
            'creator':
            joiner(creator),
            'date':
            joiner(date),
            'publisher':
            joiner(publisher),
            'language':
            joiner([LANGUAGE_ABBREVS[x] for x in language]),
            'image_link':
            j['thumbnail'][0]['id'],
            'manifest':
            j['id'],
            'manifid':
            manifid,
            'wagtail_link':
            DisplayBrowse.mk_wagtail_object_url(
                'social-scientists-map-chicago', manifid
            ),
        }
        return output

    def get_cbrowse_items(collection_slug: str,
                          browse: str,
                          browse_type: str,
                          modify=GeneralPurpose.noop,
                          func=GeneralPurpose.identity) -> list:
        """
        Retrieve cluster browse links from IIIF server.

        Args:
            collection_slug: slugified name of collection, string

            browse: name of browse, string

            browse_type: name of browse type, string

            modify: response modifying-function for testing

            func: json-modifying function for testing

        Returns:
            A list of dictionaries with thumbnail/link content for each
            item in a given browse.
        """
        # generate link to IIIF JSON for cluster browse
        iiif_url = CBrowseURL.mk_cbrowse_url_iiif(
            collection_slug,
            browse,
            browse_type,
        )

        # retrieve browse information from IIIF server
        try:
            r = requests.get(iiif_url)
            modify(r)
            if r.status_code >= 200 and r.status_code < 300:
                j = func(r.json())
                objects = [DisplayBrowse.prepare_browse_json(
                    x, DisplayBrowse.comma_join) for x in j['items']]
                return objects
            else:
                return ''
        except requests.exceptions.RequestException:
            return ''

    def get_lbrowse_items(collection_slug: str,
                          browse: str,
                          modify=GeneralPurpose.noop,
                          func=GeneralPurpose.identity) -> list:
        """
        Retrieve list browse links from IIIF server.

        Args:
            collection_slug: slugified name of collection, string

            browse: name of browse, string

            browse_type: name of browse type, string

            modify: response modifying-function for testing

            func: json-modifying function for testing

        Returns:
            A list of dictionaries with thumbnail/link content for each
            item in a given browse.
        """
        iiif_url = LBrowseURL.mk_lbrowse_url_iiif(
            collection_slug,
            browse,
        )

        # retrieve browse information from IIIF server
        try:
            r = requests.get(iiif_url)
            modify(r)
            if r.status_code >= 200 and r.status_code < 300:
                j = func(r.json())
                objects = [DisplayBrowse.prepare_browse_json(
                    x, DisplayBrowse.comma_join) for x in j['items']]
                return objects
            else:
                return ''
        except requests.exceptions.RequestException:
            return ''


class CitationInfo():
    """
    Namespace class containing utility functions/constants for interacting with
    the citation restful service
    """

    # citation config that gets autopopulated in the Wagtail admin
    # panel when you create a new collection
    default_config = (
        'base=http://ark.lib.uchicago.edu/ark:/61001\n'
        '\n'
        '[dc]\n'
        '\turi=http://purl.org/dc/elements/1.1/\n'
        '\ttype=type\n'
        '\tidentifier=id\n'
        '\tlanguage=language\n'
        '\tcreator=author\n'
        '\tformat=medium\n'
        '\tpublisher=publisher\n'
        '\ttitle=title\n'
        '[dcterms]\n'
        '\turi=http://purl.org/dc/terms/\n'
        '\tissued=issued\n'
        '\tisPartOf=collection-title\n'
        '[bf]\n'
        '\turi=http://id.loc.gov/ontologies/bibframe/\n'
        '\tClassificationLcc=call-number\n'
        '\tDoi=DOI\n\tplace=pubisher-place\n'
        '\tscale=scale'
    )

    def get_turtle_data(manifid: str,
                        modify=GeneralPurpose.noop) -> str:
        """
        Given a collection object NOID, query the primary ARK resolver to
        obtain the Turtle data for the object, serialized in the form
        a string.  This is workaround; theoretically we would like to
        be able to get this information by directly querying the Mark
        Logic server, but Mark Logic has not yet added this feature.
        (Supposedly it will have that feature in the future, however.
        Stay tuned.)

        Args:
            manifid: ARK NOID, string

            modify: response modifying-function for testing

        Returns:
            Turtle data string

        """
        url = "%s%s/file.ttl" % (TURTLE_ROOT, manifid)
        try:
            r = requests.get(url)
            modify(r)
            if r.status_code >= 200 and r.status_code < 300:
                return str(r.content, "utf-8")
            else:
                return ''
        except (requests.exceptions.RequestException):
            return ''

    def get_citation(mode: str,
                     turtle_data: str,
                     config: str,
                     modify=GeneralPurpose.noop) -> str:
        """
        Query the citation restful service for citation info.  Mode can be
        bibtex, csl, ris, or xml, and the two inputs are the
        collection object Turtle data and citation config file in INI
        format (serialized as a string).

        For more info on using/maintaining the citation restful
        service, see our doc at uchicago-library.github.io.

        Args:
            mode: String representing output format

            turtle_data: Turtle data string

            config: INI config file string

        Returns:
            Dictionary containing CSL/BibTeX/RIS/XML citation
            info for use in the collection object template
        """
        r = requests.get(
            CITATION_ROOT,
            params={
                "mode": mode,
                "turtle": turtle_data,
                "config": config,
            }
        )
        modify(r)
        if r.status_code >= 200 and r.status_code < 300:
            return str(r.content, "utf-8")
        else:
            return ''

    def get_csl(turtle_data: str,
                config: str,
                modify=GeneralPurpose.noop) -> dict:
        """
        Main function to query the citation service for CSL-JSON info in
        models.py.  This is used to live-display the collection object
        citation in the object page.

        Args:
            turtle_data: turtle data, string

            config: INI config file string

        Returns:
            CSL-JSON as a Python dictionary
        """
        try:
            c = CitationInfo.get_citation("csl", turtle_data, config, modify)
            return json.loads(c)
        except (json.JSONDecodeError,
                TypeError,
                requests.exceptions.RequestException):
            return ''

    def get_zotero(turtle_data: str,
                   config: str,
                   modify=GeneralPurpose.noop) -> str:
        """
        Main function to query the citation service for Zotero harvesting
        meta tags in models.py.

        Args:
            turtle_data: turtle data, string

            config: INI config file string

        Returns:
            Zotero harvesting HTML
        """
        try:
            return CitationInfo.get_citation("zotero",
                                             turtle_data,
                                             config,
                                             modify=modify)
        except requests.exceptions.RequestException:
            return ''

    # def csl_json_to_html(csl_json: dict, style: str) -> str:
    #     """
    #     Render CSL-JSON in HTML for the collection object template.  Note
    #     that this uses code from the citeproc-py library, which,
    #     annoyingly, insists on reading the CSL style files off disk.
    #     Those style files are located at lib_collections/csl.  See
    #     path constants below.

    #     Args:
    #         csl_json: CSL-JSON entry, dictionary

    #         style: path on serverside filesystem to CSL style file

    #     Returns:
    #         Citation HTML
    #     """
    #     if not os.path.isfile(style):
    #         return ''
    #     else:
    #         try:
    #             bib_source = CiteProcJSON(csl_json)
    #             bib_style = CitationStylesStyle(style, validate=False)
    #             bibliography = CitationStylesBibliography(
    #                 bib_style, bib_source, formatter.html
    #             )

    #             for obj in csl_json:
    #                 # Gets the object's id and makes it into citation item.
    #                 citation = Citation([CitationItem(obj['id'])])
    #                 bibliography.register(citation)

    #             html = ""
    #             for ms in bibliography.bibliography():
    #                 lst = list(OrderedDict.fromkeys(ms.split()))
    #                 s = ' '.join(lst)
    #                 html += (s + "<br>")

    #             return html
    #         except (AttributeError, TypeError):
    #             return ''

    def citation_export(mode: str,
                        turtle_data: str,
                        config: str,
                        modify=GeneralPurpose.noop):
        """
        Create link to display BibTeX or RIS citation as plaintext in the
        browser by forwarding citation information to the
        /citation_display route.  See citation_display view in
        views.py for more info.

        Args:
            mode: Output format string

            turtle_data: Turtle data string

            config: INI config string

            modify: testing-only function for modifying responses

        Returns:
            URL to display the relevant citation in plaintext
        """
        c = CitationInfo.get_citation(mode,
                                      turtle_data,
                                      config,
                                      modify=modify)
        if c:
            query_params = {"content": c}
            query_string = urlencode(query_params)
            output = "/citation_display?" + query_string
            return output
        else:
            return ''

    def get_bibtex(turtle_data, config, modify=GeneralPurpose.noop):
        """
        Main function to create link to display BibTeX citation in
        models.py.

        Args:
            turtle_data: Turtle data string

            config: INI config string

            modify: testing-only function for modifying responses

        Returns:
            BibTeX viewing URL
        """
        try:
            return CitationInfo.citation_export("bibtex",
                                                turtle_data,
                                                config,
                                                modify=modify)
        except requests.exceptions.RequestException:
            return ''

    def get_ris(turtle_data,
                config,
                modify=GeneralPurpose.noop):
        """
        Main function to create link to display RIS citation in models.py.

        Args:
            turtle_data: Turtle data string,

            config: INI config string

            modify: testing-only function for modifying responses

        Returns:
            RIS viewing URL
        """
        try:
            return CitationInfo.citation_export("ris",
                                                turtle_data,
                                                config,
                                                modify=modify)
        except requests.exceptions.RequestException:
            return ''


class IIIFDisplay:

    def mk_manifest_url(manifid: str) -> str:
        """
        Create URL for an object's IIIF manifest.

        Args:
            manifid: ARK NOID, string

        Returns:
            IIIF Manifest URL
        """
        return "%s/object/ark:/61001/%s.json" % (IIIF_PREFIX, manifid)

    def mk_viewer_url(manifid: str) -> str:
        """
        Create Universal Viewer URL for a collection object.

        Args:
            manifid: ARK NOID, string

        Returns:
            Url for Universal Viewer viewing the relevant object
        """
        return IIIF_VIEWER_PREFIX + IIIFDisplay.mk_manifest_url(manifid)

    def test_url(url: str,
                 modify=GeneralPurpose.noop) -> str:
        """
        Test that an object manifest exists.

        Args:
            url: url to be tested, string

            modify: testing-only function for modifying responses

        Returns:
            the input URL if it is valid, and the empty string otherwise
        """
        try:
            r = requests.get(url)
            modify(r)
            if r.status_code >= 200 and r.status_code < 300:
                return url
            else:
                return ''
        except (requests.exceptions.RequestException, AttributeError):
            return ''

    def get_viewer_url(manifid: str,
                       modify=GeneralPurpose.noop) -> str:
        """
        Test manifest URL and if it is valid, return a URL for the
        Universal Viewer for that object.

        Args:
            manifid: ARK NOID, string

            modify: testing-only function for modifying responses
        """

        test = IIIFDisplay.test_url(IIIFDisplay
                                    .mk_manifest_url(manifid),
                                    modify=modify)
        if test:
            url = IIIFDisplay.mk_viewer_url(manifid)
            return IIIFDisplay.test_url(url)
        else:
            return ''


class Testing():
    """
    Namespace class containing helper functions and constants for
    testing purposes only.  The functions in this class are intended
    to be the modify/func inputs to the various functions that
    retrieve data from over the web in utils.py and marklogic.py.
    """

    # sample turtle data for testing
    example = (
        '@base <http://ark.lib.uchicago.edu/ark:/61001/> .\n'
        '@prefix bf: <http://id.loc.gov/ontologies/bibframe/> .\n'
        '@prefix dc: <http://purl.org/dc/elements/1.1/> .\n'
        '@prefix dcterms: <http://purl.org/dc/terms/> .\n'
        '@prefix edm: <http://www.europeana.eu/schemas/edm/> .\n'
        '@prefix erc: <http://purl.org/kernel/elements/1.1/> .\n'
        '@prefix ore: <http://www.openarchives.org/ore/terms/> .\n'
        '@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n'
        '\n'
        '</digital_collections/IIIF_Files/social_scientists_maps/'
        'G4104-C6-2W9-1920z-U5/G4104-C6-2W9-1920z-U5.dc.xml> a ore:Proxy ;\n'
        '    dc:format "application/xml" ;\n'
        '    ore:proxyFor </digital_collections/IIIF_Files/maps/chisoc/'
        'G4104-C6-2W9-1920z-U5> ;\n'
        '    ore:proxyIn </aggregation/digital_collections/'
        'IIIF_Files/maps/chisoc/G4104-C6-2W9-1920z-U5> .\n'
        '\n'
        '</rem/digital_collections/IIIF_Files/maps/chisoc/'
        'G4104-C6-2W9-1920z-U5> a ore:ResourceMap ;\n'
        '    dcterms:created "2020-06-22T15:39:04.791815"^^xsd:dateTime ;\n'
        '    dcterms:creator <http://library.uchicago.edu> ;\n'
        '    dcterms:modified "2020-06-22T15:39:04.791815"^^xsd:dateTime ;\n'
        '    ore:describes </aggregation/digital_collections/IIIF_Files/'
        'maps/chisoc/G4104-C6-2W9-1920z-U5> .\n'
        '\n'
        '<https://repository.lib.uchicago.edu/digitalcollections/maps/chisoc>'
        'dcterms:hasPart </digital_collections/IIIF_Files/maps/chisoc/'
        'G4104-C6-2W9-1920z-U5> .\n'
        '\n'
        '</aggregation/digital_collections/IIIF_Files/maps/chisoc/'
        'G4104-C6-2W9-1920z-U5> a ore:Aggregation ;\n'
        '    dcterms:created "2020-06-22T15:39:04.791815"^^xsd:dateTime ;\n'
        '    dcterms:modified "2020-06-22T15:39:04.791815"^^xsd:dateTime ;\n'
        '    edm:aggregatedCHO </digital_collections/IIIF_Files/maps/chisoc/G4104-C6-2W9-1920z-U5> ;\n'
        '    edm:dataProvider "The University of Chicago Library" ;\n'
        '    edm:isShownAt "http://pi.lib.uchicago.edu/1001/maps/chisoc/G4104-C6-2W9-1920z-U5" ;\n'
        '    edm:isShownBy </digital_collections/IIIF_Files/maps/chisoc/G4104-C6-2W9-1920z-U5.tif> ;\n;'
        '    edm:object </digital_collections/IIIF_Files/maps/chisoc/G4104-C6-2W9-1920z-U5.tif> ;\n'
        '    edm:provider "The University of Chicago Library" ;\n'
        '    edm:rights <https://rightsstatements.org/page/InC/1.0/?language=en> ;\n'
        '    ore:isDescribedBy </rem/digital_collections/IIIF_Files/maps/chisoc/G4104-C6-2W9-1920z-U5> .\n'
        '\n'
        '</digital_collections/IIIF_Files/maps/chisoc/G4104-C6-2W9-1920z-U5> a edm:ProvidedCHO ;\n'
        '    bf:ClassificationLcc "G4104.C6:2W9 1920z .U5" ;\n'
        '    bf:Local "http://pi.lib.uchicago.edu/1001/cat/bib/3451312" ;\n'
        '    bf:scale "Scale [ca. 1:8,000]" ;\n'
        '    dc:date "1920/1929" ;\n'
        '    dc:description "Blue line print.",\n'
        '        "Master and use copy. Digital master created according to Benchmark for '
        'Faithful Reproductions of Monographs and Serials, Version 1. Digital Library Federation, '
        'December 2002. http://www.diglib.org/standards/bmarkfin.htm",\n'
        '        "Shows residential area, vacant area, commercial frontage, railroad property, '
        'and transit lines." ;\n'
        '    dc:format "1 map",\n'
        '        "45 x 62 cm" ;\n'
        '    dc:identifier "http://pi.lib.uchicago.edu/1001/maps/chisoc/G4104-C6-2W9-1920z-U5" ;\n'
        '    dc:language "English" ;\n'
        '    dc:publisher "Dept. of Sociology" ;\n'
        '    dc:rights <http://creativecommons.org/licenses/by-sa/4.0/> ;\n'
        '    dc:title "Woodlawn Community /" ;\n'
        '    dc:type "Maps" ;\n'
        '    dcterms:hasFormat "Print version" ;\n'
        '    dcterms:isPartOf <https://repository.lib.uchicago.edu/digitalcollections/maps/chisoc> ;\n'
        '    erc:what "Woodlawn Community /" ;\n'
        '    erc:when "1920/1929" ;\n'
        '    erc:where </digital_collections/IIIF_Files/maps/chisoc/G4104-C6-2W9-1920z-U5> ;\n'
        '    erc:who "University of Chicago. Department of Sociology." ;\n'
        '    edm:currentLocation "Map Collection Reading Room (Room 370)" ;\n'
        '    edm:type "IMAGE" ;\n'
        '    edm:year "1920/1929" .\n'
        '\n'
    )

    # default config from CitationInfo is also useful for testing
    default_config = CitationInfo.default_config

    def bring_website_down(response):
        """
        Throw a ConnectionError.

        Args:
            response: HTTP response

        Returns:
            Side effect-ful function; no return value.
        """
        raise requests.exceptions.ConnectionError(
            "Testing: pretending the server is down"
        )

    def change_status_code(code: int):
        """
        Take an HTTP response and mutate its status code to be that of the
        input.

        Args:
            code: (curried) status code, integer

            response: (curried) HTTP response

        Returns:
            Side effect-ful; no return value.

        """
        def partial(response):
            response.status_code = code
        return partial

    def break_json(response):
        """
        Take an HTTP response and make its content syntactically invalid.
        Assumes the body of the response is JSON.

        Args:
            response: HTTP response

        Returns:
            Side effect-ful; no return value.
        """
        response._content += b'}'

    def unexpected_json(response):
        """
        Take an HTTP response and replace its content with a dictionary
        whose structure is not what the code expects.  Assumes the
        body of the response is (intended to be) JSON.

        Args:
            response: HTTP response

        Returns:
            Side effect-ful; no return value.
        """
        new = b'{"random_dictionary": [{"with": 4}, {"stuff": false}]}'
        response._content = new

    # constant function to empty SparQL query

    # Args:
    #     anything

    # Returns: an unexpected JSON dictionary
    empty_sparql = GeneralPurpose.k(
        {'head': {'vars': []}, 'results': {'bindings': []}}
    )


class Permissions():
    """
    Namespace class containing helper functions for determining
    permissions in a collection page.
    """

    def get_users_ip(request):
        return Result.default(
            Result.lookup("REMOTE_ADDR", request.environ))

    def shibbed_cnetid(request):
        return Result.default(
            Result.lookup("REMOTE_USER", request.environ))

    def shibbed_in(request):
        return bool(Permissions.shibbed_cnetid(request))

    CAMPUS_SUBNETS = [
        "128.135.43.0/24",
        "128.135.53.0/24",
        "128.135.55.0/24",
        "128.135.153.0/24",
        "128.135.159.0/24",

        "128.135.0.0/16",
        "205.208.0.0/17",
        "165.68.0.0/16",
        "192.170.192.0/19",
        "10.0.0.0/8",
        "172.16.0.0/12",
        "192.168.0.0/16",

        "165.68.0.0/16",
        "64.107.48.0/23",
    ]

    def in_subnet(ip_string, subnet_string):
        input_ip = ipaddress.ip_address(ip_string)
        subnet = ipaddress.ip_network(subnet_string)
        return input_ip in subnet

    def on_campus(ip_string, subnets=CAMPUS_SUBNETS):
        the_possibilities = [Permissions.in_subnet(ip_string, x)
                             for x in subnets]
        return any(the_possibilities)

    def open_show_player(perm, request):
        return perm == "Open"

    def campus_show_player(perm, request):
        perm_is_campus = perm == "Campus"
        user_ip = Permissions.get_users_ip(request)
        user_on_campus = Permissions.on_campus(user_ip)
        user_shibbed = Permissions.shibbed_cnetid(request)
        return perm_is_campus and (user_on_campus or user_shibbed)

    def campus_crossout_player(perm, request):
        perm_is_campus = perm == "Campus"
        user_ip = Permissions.get_users_ip(request)
        user_on_campus = Permissions.on_campus(user_ip)
        user_shibbed = Permissions.shibbed_cnetid(request)
        return (perm_is_campus and
                ((not user_on_campus) and (not user_shibbed)))

    def restricted_player(perm, request):
        return perm == "Restricted"
