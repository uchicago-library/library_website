from base.utils import get_xml_from_directory_api
from django.core import management
from django.test import TestCase
from io import StringIO
from lxml import etree
from public.models import StandardPage
from .models import StaffPage, StaffPageEmailAddresses, StaffPageLibraryUnits, StaffPagePhoneFacultyExchange
from staff.utils import get_all_library_cnetids_from_directory, get_individual_info_from_directory
from units.models import UnitPage
from wagtail.wagtailcore.models import Page

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

    def assertInfoEqual(self, a, b):
        for field in ['cnetid', 'officialName', 'displayName']:
            if not a[field] == b[field]:
                return False

        tds_a = sorted([a['title_department_subdepartments']])
        tds_b = sorted([b['title_department_subdepartments']])

        if not len(tds_a) == len(tds_b):
            return False

        t = 0
        while t < len(tds_a):
            if not tds_a[t] == tds_b[t]:
                return False
            t = t + 1

        tds_a = sorted(a['title_department_subdepartments_dicts'], key = lambda t: t['title'] + t['department'])
        tds_b = sorted(b['title_department_subdepartments_dicts'], key = lambda t: t['title'] + t['department'])

        if not len(tds_a) == len(tds_b):
            return False

        t = 0
        while t < len(tds_a):
            for field in ['department', 'title', 'email', 'facultyexchange', 'phone']:
                if not tds_a[t][field] == tds_b[t][field]:
                    return False
            t = t + 1

        return True

    def test_get_individual_info_from_directory(self):
        self.maxDiff = None

        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <responseData>
          <response>Success</response>
          <totalResults>1</totalResults>
          <individuals>
            <individual>
              <name>Scooter McDanger</name>
              <displayName>Scooter McDanger</displayName>
              <cnetid>scootermcdanger</cnetid>
              <chicagoid>12345678X</chicagoid>
              <contacts>
                <contact>
                  <title>Programmer Analyst</title>
                  <division>
                    <name>Library</name>
                    <resources>
                      <directoryURL>https://directory.uchicago.edu/organizations/16?type=divisions</directoryURL>
                      <xmlURL>https://directory.uchicago.edu/api/v2/divisions/16</xmlURL>
                    </resources>
                  </division>
                  <email>scootermcdanger@uchicago.edu</email>
                  <phone>(773) 702-1234</phone>
                  <facultyExchange>JRL 220</facultyExchange>
                </contact>
              </contacts>
              <resources>
                <directoryURL>https://directory.uchicago.edu/individuals/12345678X</directoryURL>
                <xmlURL>https://directory.uchicago.edu/api/v2/individuals/12345678X</xmlURL>
              </resources>
            </individual>
          </individuals>
        </responseData>
        """

        info = {
            'cnetid': 'scootermcdanger',
            'officialName': 'Scooter McDanger',
            'displayName': 'Scooter McDanger',
            'title_department_subdepartments': {'Programmer Analyst\nLibrary\nJRL 220\n773-702-1234'},
            'title_department_subdepartments_dicts': [{
                'title': 'Programmer Analyst',
                'email': 'scootermcdanger@uchicago.edu',
                'facultyexchange': 'JRL 220',
                'phone': '773-702-1234'
            }]
        }

        self.assertInfoEqual(get_individual_info_from_directory(xml), info)

class StaffPageSupervisors(TestCase):
    def setUp(self):
        try:
            welcome = Page.objects.get(path='00010001')
        except:
            root = Page.objects.create(
                depth=1,
                path='0001',
                slug='root',
                title='Root')

            welcome = Page(
                path='00010001',
                slug='welcome',
                title='Welcome')
            root.add_child(instance=welcome)

        # StaffPages
        official_supervisor = StaffPage(
            cnetid='official_supervisor', 
            slug='official-supervisor', 
            title='Official Supervisor')
        welcome.add_child(instance=official_supervisor)

        another_official_supervisor = StaffPage(
            cnetid='another_official_supervisor', 
            slug='another-official-supervisor', 
            title='Another Official Supervisor')
        welcome.add_child(instance=another_official_supervisor)

        director = StaffPage(
            cnetid='director', 
            slug='director', 
            title='Director')
        welcome.add_child(instance=director)

        supervisor_override = StaffPage(
            cnetid='supervisor_override', 
            slug='supervisor-override',
            title='Supervisor Override')
        welcome.add_child(instance=supervisor_override)

        employee_override = StaffPage(
            cnetid='employee_override',
            slug='employee_override',
            supervisor_override=supervisor_override,
            title='Employee Override')
        welcome.add_child(instance=employee_override)

        employee_no_override = StaffPage(
            cnetid='employee_no_override',
            slug='employee_no_override',
            title='Employee No Override')
        welcome.add_child(instance=employee_no_override)

        employee_two_units = StaffPage(
            cnetid='employee_two_units',
            slug='employee_two_units',
            title='Employee Two Units')
        welcome.add_child(instance=employee_two_units)

        content_specialist = StaffPage(
            cnetid='content_specialist',
            slug='content-specialist',
            title='Content Specialist'
        )
        welcome.add_child(instance=content_specialist)

        editor = StaffPage(
            cnetid='editor',
            slug='editor',
            title='Editor')
        welcome.add_child(instance=editor)

        page_maintainer = StaffPage(
            cnetid='page_maintainer',
            slug='page-maintainer',
            title='Page Maintainer')
        welcome.add_child(instance=page_maintainer)

        # UnitPages
        unit_division = UnitPage(
            department_head=director,
            editor=editor,
            page_maintainer=page_maintainer,
            slug='unit-division',
            title='Unit Division'
        )
        welcome.add_child(instance=unit_division)

        unit_one = UnitPage(
            department_head=official_supervisor,
            display_in_dropdown=True,
            editor=editor,
            page_maintainer=page_maintainer,
            slug='unit-one',
            title='Unit One')
        unit_division.add_child(instance=unit_one)

        unit_two = UnitPage(
            department_head=another_official_supervisor,
            editor=editor,
            page_maintainer=page_maintainer,
            slug='unit-two',
            title='Unit Two')
        unit_division.add_child(instance=unit_two)

        # StandardPage
        standard_page = StandardPage(
            content_specialist=content_specialist,
            editor=editor,
            page_maintainer=page_maintainer,
            slug='standard-page',
            title='Standard Page',
            unit=unit_one
        )
        welcome.add_child(instance=standard_page)

        # assign staff to units
        StaffPageLibraryUnits.objects.create(
            page=director,
            library_unit=unit_division)

        StaffPageLibraryUnits.objects.create(
            page=official_supervisor,
            library_unit=unit_one)

        StaffPageLibraryUnits.objects.create(
            page=employee_no_override, 
            library_unit=unit_one)

        StaffPageLibraryUnits.objects.create(
            page=employee_override, 
            library_unit=unit_one)

        StaffPageLibraryUnits.objects.create(
            page=employee_two_units, 
            library_unit=unit_one)

        StaffPageLibraryUnits.objects.create(
            page=employee_two_units, 
            library_unit=unit_two)

    def test_official_supervisor(self):
        self.assertEqual(StaffPage.objects.get(cnetid='employee_no_override').get_supervisors, [StaffPage.objects.get(cnetid='official_supervisor')])

    def test_supervisor_override(self):
        self.assertEqual(StaffPage.objects.get(cnetid='employee_override').get_supervisors, [StaffPage.objects.get(cnetid='supervisor_override')])

    def test_employee_in_two_units(self):
        self.assertEqual(StaffPage.objects.get(cnetid='employee_two_units').get_supervisors, [StaffPage.objects.get(cnetid='official_supervisor'), StaffPage.objects.get(cnetid='another_official_supervisor')])

    def test_department_head_supervisor(self):
        self.assertEqual(StaffPage.objects.get(cnetid='official_supervisor').get_supervisors, [StaffPage.objects.get(cnetid='director')])

    def test_unit_one_child_of_division(self):
        self.assertEqual(UnitPage.objects.get(slug='unit-one').get_parent().specific, UnitPage.objects.get(slug='unit-division'))
    

class ListStaffWagtail(TestCase):
    def setUp(self):
        root = Page.objects.create(
            depth=1,
            path='0001',
            slug='root',
            title='Root')

        welcome = Page(
            path='00010001',
            slug='welcome',
            title='Welcome')
        root.add_child(instance=welcome)

        chas = StaffPage(
            cnetid='chas',
            employee_type=3,
            slug='charles-blair',
            position_status=1,
            position_title='Director, Digital Library Development Center',
            supervises_students=True,
            title='Charles Blair')
        welcome.add_child(instance=chas)

        bbusenius = StaffPage(
            cnetid='bbusenius',
            employee_type=3,
            slug='brad-busenius',
            position_status=1,
            position_title='Web Administrator',
            supervisor_override=chas,
            supervises_students=False,
            title='Brad Busenius')
        welcome.add_child(instance=bbusenius)

        byrne = StaffPage(
            cnetid='byrne',
            employee_type=3,
            slug='maura-byrne',
            position_status=1,
            position_title='Applications Systems Analyst/Programmer',
            supervises_students=False,
            title='Maura Byrne')
        welcome.add_child(instance=byrne)

        eliminated_position = StaffPage(
            cnetid='eliminated-position',
            slug='eliminated-position',
            position_status=3,
            title='Eliminated Position')
        welcome.add_child(instance=eliminated_position)

        elong = StaffPage(
            cnetid='elong',
            slug='elisabeth-long',
            position_status=3,
            title='Elisabeth Long')
        welcome.add_child(instance=elong)

        digital_services = UnitPage(
            department_head=elong,
            editor=elong,
            page_maintainer=elong,
            slug='digital-services',
            title='Digital Services')
        welcome.add_child(instance=digital_services)

        dldc = UnitPage(
            department_head=chas,
            editor=chas,
            page_maintainer=chas,
            slug='dldc',
            title='Digital Library Development Center')
        digital_services.add_child(instance=dldc)

        jej = StaffPage(
            cnetid='jej',
            employee_type=3,
            slug='john-jung',
            position_status=1,
            position_title='Programmer/Analyst',
            supervisor_override=chas,
            supervises_students=False,
            title='John Jung')
        welcome.add_child(instance=jej)

        StaffPageEmailAddresses.objects.create(
            page=jej,
            email='jej@uchicago.edu')

        StaffPageEmailAddresses.objects.create(
            page=jej,
            email='jej@jej.com')

        StaffPagePhoneFacultyExchange.objects.create(
            page=jej,
            phone_number='773-702-1234',
            faculty_exchange='JRL 100')

        StaffPagePhoneFacultyExchange.objects.create(
            page=jej,
            phone_number='773-834-1234',
            faculty_exchange='JRL 101')

        StaffPageLibraryUnits.objects.create(
            page=jej,
            library_unit=dldc)

        StaffPageLibraryUnits.objects.create(
            page=jej,
            library_unit=digital_services)

        kzadrozny = StaffPage(
            cnetid='kzadrozny',
            employee_type=3,
            slug='kathy-zadrozny',
            position_status=1,
            position_title='Web Developer and Graphic Design Specialist',
            supervisor_override=chas,
            supervises_students=True,
            title='Kathy Zadrozny')
        welcome.add_child(instance=kzadrozny)

        tyler = StaffPage(
            cnetid='tyler',
            employee_type=3,
            slug='tyler-danstrom',
            position_status=1,
            position_title='Programmer/Analyst',
            supervisor_override=chas,
            supervises_students=False,
            title='Tyler Danstrom')
        welcome.add_child(instance=tyler)

    def run_command(self, **options):
        output = StringIO()
        management.call_command('list_staff_wagtail', stdout=output, **options)
        output.seek(0)

        records = []
        for line in output:
            records.append(line.split("\t"))

        return records
            
    def test_cnetid_returns_one_record(self):
        records = self.run_command(cnetid='jej')
        self.assertEqual(len(records), 1)

    def test_cnetid_returns_correct_name(self):
        records = self.run_command(cnetid='jej')
        self.assertEqual(records[0][2], 'John Jung (jej)')

    def test_position_status(self):
        records = self.run_command(position_status='Active')
        self.assertEqual(len(records), 6)

    def test_supervises_students(self):
        records = self.run_command(supervises_students=True)
        self.assertEqual(len(records), 2)

    def test_supervisor_cnetid(self):
        records = self.run_command(supervisor_cnetid='chas')
        self.assertEqual(len(records), 4)

    def test_title(self):
        records = self.run_command(title='Programmer/Analyst')
        self.assertEqual(len(records), 2)

    def test_report_column_count(self):
        records = self.run_command(cnetid='jej')
        self.assertEqual(len(records[0]), 11)

    def test_report_columns_name_and_cnetid(self):
        records = self.run_command(cnetid='jej')
        self.assertEqual(records[0][2], 'John Jung (jej)')

    def test_report_columns_position_title(self):
        records = self.run_command(cnetid='jej')
        self.assertEqual(records[0][3], 'Programmer/Analyst')

    def test_report_columns_position_title(self):
        records = self.run_command(cnetid='jej')
        self.assertEqual(set(records[0][4].split('|')), set(('jej@uchicago.edu', 'jej@jej.com')))

    def test_report_columns_faculty_exchange_phone_number(self):
        records = self.run_command(cnetid='jej')
        self.assertEqual(set(records[0][5].split('|')), set(('JRL 100,773-702-1234', 'JRL 101,773-834-1234')))

    def test_report_columns_units(self):
        records = self.run_command(cnetid='jej')
        self.assertEqual(records[0][6], 'Digital Library Development Center|Digital Services')

    def test_report_columns_employee_type(self):
        records = self.run_command(cnetid='jej')
        self.assertEqual(records[0][7], 'IT')

    def test_report_columns_supervises_students(self):
        records = self.run_command(cnetid='jej')
        self.assertEqual(records[0][8], 'False')

    def test_report_columns_position_status(self):
        records = self.run_command(cnetid='jej')
        self.assertEqual(records[0][9], 'Active')

    def test_report_columns_supervisor_name_and_cnetid(self):
        records = self.run_command(cnetid='jej')
        self.assertEqual(records[0][10].rstrip(), 'Charles Blair (chas)')
       
     
