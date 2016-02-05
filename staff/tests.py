from base.utils import get_xml_from_directory_api
from django.test import TestCase
from io import StringIO
from lxml import etree
from staff.utils import get_all_library_cnetids_from_directory

class UniversityDirectoryTestCase(TestCase):
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

    def test_individual_xml_validates(self):
        dtd = etree.DTD(StringIO("""
        <!ELEMENT responseData    (response, totalResults, individuals)>
        <!ELEMENT response        (#PCDATA)>
        <!ELEMENT totalResults    (#PCDATA)>
        <!ELEMENT individuals     (individual+)>
        <!ELEMENT individual      (name, displayName, cnetid, chicagoid, contacts, resources)>
        <!ELEMENT name            (#PCDATA)>
        <!ELEMENT displayName     (#PCDATA)>
        <!ELEMENT cnetid          (#PCDATA)>
        <!ELEMENT chicagoid       (#PCDATA)>
        <!ELEMENT contacts        (contact)>
        <!ELEMENT contact         (title, division, department, subDepartment, email, phone, facultyExchange)>
        <!ELEMENT title           (#PCDATA)>
        <!ELEMENT division        (name, resources)>
        <!ELEMENT resources       (directoryURL, xmlURL)>
        <!ELEMENT directoryURL    (#PCDATA)>
        <!ELEMENT xmlURL          (#PCDATA)>
        <!ELEMENT department      (name, resources)>
        <!ELEMENT subDepartment   (name, resources)>
        <!ELEMENT email           (#PCDATA)>
        <!ELEMENT phone           (#PCDATA)>
        <!ELEMENT facultyExchange (#PCDATA)>
        """))

        cnetids = get_all_library_cnetids_from_directory()
        root = etree.XML(get_xml_from_directory_api('https://directory.uchicago.edu/api/v2/individuals/' + cnetids[0] + '.xml'))
        self.assertEqual(dtd.validate(root), True)

    def test_get_all_library_cnet_ids_from_directory_two_staff(self):
        xml_string = """<?xml version="1.0" encoding="UTF-8"?>
        <responseData>
          <response>Success</response>
          <totalResults>1</totalResults>
          <organizations>
            <organization>
              <name>Library</name>
              <type>Division</type>
              <departments>
                <department>
                  <name>Digital Services</name>
                  <resources>
                    <directoryURL>https://directory.uchicago.edu/organizations/575?type=departments</directoryURL>
                    <xmlURL>https://directory.uchicago.edu/api/v2/departments/575</xmlURL>
                  </resources>
                </department>
              </departments>
              <members>
                <member>
                  <name>Scooter McDanger</name>
                  <displayName>Scooter McDanger</displayName>
                  <cnetid>danger</cnetid>
                  <chicagoid>12345678L</chicagoid>
                  <title>Programmer/Analyst</title>
                  <email>danger@uchicago.edu</email>
                  <phone>(773) 702-1234</phone>
                  <facultyExchange>JRL 220</facultyExchange>
                  <resources>
                    <directoryURL>https://directory.uchicago.edu/individuals/12345678L</directoryURL>
                    <xmlURL>https://directory.uchicago.edu/api/v2/individuals/12345678L</xmlURL>
                  </resources>
                </member>
                <member>
                  <name>Margaret Lovelee</name>
                  <displayName>Margaret Lovelee</displayName>
                  <cnetid>lovelee</cnetid>
                  <chicagoid>12345678L</chicagoid>
                  <title>Programmer/Analyst</title>
                  <email>lovelee@uchicago.edu</email>
                  <phone>(773) 702-1234</phone>
                  <facultyExchange>JRL 220</facultyExchange>
                  <resources>
                    <directoryURL>https://directory.uchicago.edu/individuals/12345678L</directoryURL>
                    <xmlURL>https://directory.uchicago.edu/api/v2/individuals/12345678L</xmlURL>
                  </resources>
                </member>
              </members>
              <resources>
                <directoryURL>https://directory.uchicago.edu/organizations/16?type=divisions</directoryURL>
                <xmlURL>https://directory.uchicago.edu/api/v2/divisions/16</xmlURL>
              </resources>
            </organization>
          </organizations>
        </responseData>
        """

        cnetids = get_all_library_cnetids_from_directory(xml_string)

        self.assertEqual(set(cnetids), set(('lovelee', 'danger')))

        
