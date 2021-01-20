from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from citeproc.py2compat import *

import json
import sys
import os
import requests

from citeproc import CitationStylesStyle, CitationStylesBibliography
from citeproc import Citation, CitationItem
from citeproc import formatter
from citeproc.source.json import CiteProcJSON


def csl_json_to_html(csl_json, style):
    if not os.path.isfile(style):
        r = requests.get(
            'https://raw.githubusercontent.com/citation-style-language/styles/master/'+style)
        f = open(style, 'wb')
        f.write(r.content)
        f.close()
    bib_source = CiteProcJSON(csl_json)
    bib_style = CitationStylesStyle(style, validate=False)
    bibliography = CitationStylesBibliography(
        bib_style, bib_source, formatter.html)

    for obj in csl_json:
        # Gets the object's id and makes it into citation item.
        citation = Citation([CitationItem(obj['id'])])
        bibliography.register(citation)

    html = ""
    for item in bibliography.bibliography():
        html += (str(item) + "<br>")

    return html


def csl_json_to_bibtex(csl_json):

    std = ['author', 'title', 'year']

    article_terms = std + ['journal']
    book_terms = std + ['editor', 'publisher']
    booklet_terms = ['title']
    conference_terms = std + ['booktitle']
    inbook_terms = book_terms + ['chapter', 'pages']
    mastersthesis_terms = std + ['school']
    proceedings_terms = booklet_terms + ['year']
    techreport_terms = std + ['institution']
    unpublished_terms = booklet_terms + ['author', 'note']

    bibtex_dict = {'article': article_terms,
                   'book': book_terms,
                   'booklet': booklet_terms,
                   'conference': conference_terms,
                   'inbook': inbook_terms,
                   'incollection': conference_terms,
                   'inproceedings': conference_terms,
                   'manual': booklet_terms,
                   'mastersthesis': mastersthesis_terms,
                   'phdthesis': mastersthesis_terms,
                   'proceedings': proceedings_terms,
                   'techreport': techreport_terms,
                   'unpublished': unpublished_terms
                   }

    bibtex_str = ""
    for obj in csl_json:

        json_terms = list(obj)
        if 'type' in json_terms:
            json_terms.remove('type')
        if 'id' in json_terms:
            json_terms.remove('id')

        entry_type = obj['type']
        if entry_type in list(bibtex_dict):
            if all(x in json_terms for x in bibtex_dict[entry_type]):
                bibtex_str += "@%s{%s" % (entry_type, obj['id'])
                for term in json_terms:
                    term_val = obj[term]
                    tmp_bibtex_str += ",\n\t%s = {%s}" % (term, term_val)
                bibtex_str += "\n}\n\n"
                continue

            else:
                print("Missing terms in entry type '%s'.", (entry_type))
                print("Parsing JSON as miscellaneous.")

        bibtex_str += "@misc{%s" % (obj['id'])
        for term in json_terms:
            term_val = obj[term]
            bibtex_str += ",\n\t%s = {%s}" % (term, term_val)
        bibtex_str += "\n}\n\n"

    return bibtex_str
