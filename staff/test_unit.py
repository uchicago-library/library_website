import os
import time

from base.utils import get_xml_from_directory_api
from django.core import management
from django.test import TestCase
from io import StringIO
from lxml import etree
from openpyxl import load_workbook
from public.models import StandardPage
from .models import StaffPage, StaffPageEmailAddresses, StaffPageLibraryUnits, StaffPagePhoneFacultyExchange
from staff.utils import get_all_library_cnetids_from_directory, get_individual_info_from_directory
from tempfile import NamedTemporaryFile
from units.models import UnitPage
from wagtail.core.models import Page

def print_test_time_elapsed(method):
    """
    Utility method for print verbalizing test suite, prints out
    time taken for test and functions name, and status
    """
    def run(*args, **kw):
        ts = time.time()
        print('\n\ttesting function %r' % method.__name__)
        method(*args, **kw)
        te = time.time()
        print('\t[OK] in %r %2.2f sec' % (method.__name__, te - ts))

    return run

class UniversityDirectoryTestCase(TestCase):
    @print_test_time_elapsed
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

    @print_test_time_elapsed
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
    @print_test_time_elapsed
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

    @print_test_time_elapsed
    def test_supervisor_relationships(self):
        # official supervisor
        self.assertEqual(StaffPage.objects.get(cnetid='employee_no_override').get_supervisors, [StaffPage.objects.get(cnetid='official_supervisor')])
 
        # supervisor override
        self.assertEqual(StaffPage.objects.get(cnetid='employee_override').get_supervisors, [StaffPage.objects.get(cnetid='supervisor_override')])

        # employee in two units
        self.assertEqual(StaffPage.objects.get(cnetid='employee_two_units').get_supervisors, [StaffPage.objects.get(cnetid='official_supervisor'), StaffPage.objects.get(cnetid='another_official_supervisor')])

        # department head supervisor
        self.assertEqual(StaffPage.objects.get(cnetid='official_supervisor').get_supervisors, [StaffPage.objects.get(cnetid='director')])

        # one child of division.
        self.assertEqual(UnitPage.objects.get(slug='unit-one').get_parent().specific, UnitPage.objects.get(slug='unit-division'))
    

class ListStaffWagtail(TestCase):
    @print_test_time_elapsed
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

        chas = StaffPage(
            cnetid='chas',
            employee_type=3,
            slug='charles-blair',
            position_eliminated=False,
            position_title='Director, Digital Library Development Center',
            supervises_students=True,
            title='Charles Blair')
        welcome.add_child(instance=chas)

        bbusenius = StaffPage(
            cnetid='bbusenius',
            employee_type=3,
            slug='brad-busenius',
            position_eliminated=False,
            position_title='Web Administrator',
            supervisor_override=chas,
            supervises_students=False,
            title='Brad Busenius')
        welcome.add_child(instance=bbusenius)

        byrne = StaffPage(
            cnetid='byrne',
            employee_type=3,
            slug='maura-byrne',
            position_eliminated=False,
            position_title='Applications Systems Analyst/Programmer',
            supervises_students=False,
            title='Maura Byrne')
        welcome.add_child(instance=byrne)

        eliminated_position = StaffPage(
            cnetid='eliminated-position',
            slug='eliminated-position',
            position_eliminated=False,
            title='Eliminated Position')
        welcome.add_child(instance=eliminated_position)

        elong = StaffPage(
            cnetid='elong',
            slug='elisabeth-long',
            position_eliminated=False,
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
            position_eliminated=False,
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
            position_eliminated=False,
            position_title='Web Developer and Graphic Design Specialist',
            supervisor_override=chas,
            supervises_students=True,
            title='Kathy Zadrozny')
        welcome.add_child(instance=kzadrozny)

        tyler = StaffPage(
            cnetid='tyler',
            employee_type=3,
            slug='tyler-danstrom',
            position_eliminated=False,
            position_title='Programmer/Analyst',
            supervisor_override=chas,
            supervises_students=False,
            title='Tyler Danstrom')
        welcome.add_child(instance=tyler)

    def run_command(self, **options):
        tempfile = NamedTemporaryFile(delete=False, suffix='.xlsx')
        options.update({
            'filename': tempfile.name,
            'output_format': 'excel'
        })
        management.call_command('list_staff_wagtail', **options)

        wb = load_workbook(tempfile.name)
        ws = wb.active
        os.unlink(tempfile.name)

        return [[cell.value for cell in row] for row in ws.iter_rows(min_row=2)]
       
    @print_test_time_elapsed
    def test_report_columns(self):
        records = self.run_command(cnetid='jej')

        # column count
        self.assertEqual(len(records[0]), 13)

        # row count
        self.assertEqual(len(records), 1)

        # name and cnetid
        self.assertEqual(records[0][2], 'John Jung (jej)')

        # position title
        self.assertEqual(records[0][3], 'Programmer/Analyst')

        # emails
        self.assertEqual(set(records[0][4].split('|')), set(('jej@uchicago.edu', 'jej@jej.com')))

        # faculty exchange, phone number pairs
        self.assertEqual(set(records[0][5].split('|')), set(('JRL 100,773-702-1234', 'JRL 101,773-834-1234')))

        # units
        self.assertEqual(set(records[0][6].split('|')), set(['Digital Services - Digital Library Development Center', 'Digital Services']))

        # employee type
        self.assertEqual(records[0][9], 'IT')

        # supervises students
        self.assertEqual(records[0][10], 'False')

        # position eliminated
        self.assertEqual(records[0][11], 'False')

        # supervisor
        self.assertEqual(records[0][12].rstrip(), 'Charles Blair (chas)')

    @print_test_time_elapsed
    def test_report_queries(self):
        # position title
        records = self.run_command(position_title='Programmer/Analyst')
        self.assertEqual(len(records), 2)
    
        # supervisor
        records = self.run_command(supervisor_cnetid='chas')
        self.assertEqual(len(records), 4)

        # supervises students
        records = self.run_command(supervises_students=True)
        self.assertEqual(len(records), 2)

