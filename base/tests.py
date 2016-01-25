from django.test import TestCase

from base.utils import get_xml_from_directory_api
from io import StringIO
from lxml import etree

class ValidXMLTestCase(TestCase):
    def test_directory_xml_validates(self):
        dtd = etree.DTD(StringIO("""
        <!ELEMENT responseData    (response, totalResults, organizations)>
        <!ELEMENT response        (#PCDATA)>
        <!ELEMENT totalResults    (#PCDATA)>
        <!ELEMENT organizations   (organization+)>
        <!ELEMENT organization    (name, type, departments, members, resources)>
        <!ELEMENT name            (#PCDATA)>
        <!ELEMENT type            (#PCDATA)>
        <!ELEMENT departments     (department+)>
        <!ELEMENT department      (name, resources)>
        <!--      name (see above) -->
        <!ELEMENT resources       (directoryURL, xmlURL)>
        <!ELEMENT directoryURL    (#PCDATA)>
        <!ELEMENT xmlURL          (#PCDATA)>
        <!ELEMENT members         (member+)>
        <!ELEMENT member          (name, displayName, cnetid, chicagoid, title, email, phone, facultyExchange, resources)>
        <!--      name (see above) -->
        <!ELEMENT displayName     (#PCDATA)>
        <!ELEMENT cnetid          (#PCDATA)>
        <!ELEMENT chicagoid       (#PCDATA)>
        <!ELEMENT title           (#PCDATA)>
        <!ELEMENT email           (#PCDATA)>
        <!ELEMENT phone           (#PCDATA)>
        <!ELEMENT facultyExchange (#PCDATA)>
        <!--      resources (see above) -->
        """))

        root = etree.XML(get_xml_from_directory_api('https://directory.uchicago.edu/api/v2/divisions/16.xml'))
        self.assertEqual(dtd.validate(root), True)




