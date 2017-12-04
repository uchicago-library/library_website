# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# import os
# os.environ['DJANGO_SETTINGS_MODULE'] = 'library_website.settings'
import re

from base.utils import get_xml_from_directory_api
from django.contrib.auth.models import User
from django.db.models import F
from openpyxl import Workbook
from staff.models import (EMPLOYEE_TYPES, POSITION_STATUS, StaffPage,
                          StaffPageLibraryUnits)
from units.models import UnitPage
from xml.etree import ElementTree

import csv
import io
import re

# need a list of all individuals.
# this thing needs to deal with VCards.


def get_all_library_cnetids_from_directory(xml_string=None):
    if not xml_string:
        xml_string = get_xml_from_directory_api(
            'https://directory.uchicago.edu/api/v2/divisions/16.xml'
        )

    # get xml element tree.
    x = ElementTree.fromstring(xml_string)

    # get cnetids.
    cnetids = set()
    for cnetid in x.findall(".//member/cnetid"):
        cnetids.add(cnetid.text)

    return sorted(list(cnetids))


def get_individual_info_from_directory(xml_string):
    x = ElementTree.fromstring(xml_string)

    info = {}

    info['cnetid'] = x.find("individuals/individual/cnetid").text

    # name is slightly more formal- e.g. "John E. Jung"
    info['officialName'] = x.find("individuals/individual/name").text

    # displayName is a bit more casual- e.g. "John Jung"
    info['displayName'] = x.find("individuals/individual/displayName").text

    #  title, department, subdepartment, building/room number, phone number:
    #  many individuals have more than one title- for example,
    #  Emily Treptow has the following two strings as titles:
    #  "Business and Economics Librarian for Instruction & Outreach"
    #  "Business & Economics Librarian for Instruction & Outreach"
    #  Show both titles, even though they're close, to encourage
    #  people to fix them in the university's system.
    #
    #  The title doesn't make sense without a department, subdepartment
    #  pair though. And many people, especially bibliographers,
    #  have three or four title/department/subdepartments.
    #
    # Also, some titles have different rooms- see Laura Ring for
    # an example. Many of those people, like Paul Belloni, will
    # have multiple phone numbers. (It looks like Paul has a phone
    # number at the SSA and at the Reg.)
    #
    # Each title gets it's own table? Each one points at a department/
    # subdepartment pair? (in it's own table...)

    info['title_department_subdepartments'] = set()
    info['title_department_subdepartments_dicts'] = []
    for vcard in x.findall("individuals/individual/contacts/contact"):
        try:
            if vcard.find('division/name').text != 'Library':
                continue
        except:
            continue

        output = []
        output_dict = {}

        try:
            title = re.sub('\s+', ' ', vcard.find('title').text).strip()
            if title:
                output.append(title)
                output_dict['title'] = title
        except:
            pass

        chunks = []
        try:
            department = re.sub(
                '\s+',
                ' ',
                vcard.find('department/name').text
            ).strip()
            if department:
                chunks.append(department)
        except:
            pass

        try:
            subdepartment = re.sub(
                '\s+',
                ' ',
                vcard.find('subDepartment/name').text
            ).strip()
            if subdepartment:
                chunks = chunks + subdepartment.split(" | ")
        except:
            pass

        try:
            email = re.sub('\s+', ' ', vcard.find('email').text).strip()
            if email:
                output_dict['email'] = email
        except:
            pass

        try:
            facultyexchange = re.sub(
                '\s+',
                ' ',
                vcard.find('facultyExchange').text
            ).strip()
            if facultyexchange:
                output.append(facultyexchange)
                output_dict['facultyexchange'] = facultyexchange
        except:
            pass

        try:
            phone = re.sub('\s+', ' ', vcard.find('phone').text).strip()
            if phone:
                chunks = re.search(
                    '^\(([0-9]{3})\) ([0-9]{3})-([0-9]{4})$',
                    phone
                )
                phone_number = chunks.group(1) + \
                    "-" + chunks.group(2) + "-" + chunks.group(3)
                output.append(phone_number)
                output_dict['phone'] = phone_number
        except:
            pass

        info['title_department_subdepartments'].add("\n".join(output))
        info['title_department_subdepartments_dicts'].append(output_dict)

    info['email'] = set()
    for vcard in x.findall("individuals/individual/contacts/contact"):
        try:
            if vcard.find('division/name').text != 'Library':
                continue
        except:
            continue

        try:
            email = re.sub('\s+', ' ', vcard.find('email').text).strip()
            if email:
                info['email'].add(email)
        except:
            pass

    info['phoneFacultyExchanges'] = set()
    info['phoneFacultyExchanges_dicts'] = []
    for vcard in x.findall("individuals/individual/contacts/contact"):
        try:
            if vcard.find('division/name').text != 'Library':
                continue
        except:
            continue

        output = []
        output_dict = {}

        try:
            facultyexchange = re.sub(
                '\s+',
                ' ',
                vcard.find('facultyExchange').text
            ).strip()
            if facultyexchange:
                output.append(facultyexchange)
                output_dict['facultyexchange'] = facultyexchange
        except:
            pass

        try:
            phone = re.sub('\s+', ' ', vcard.find('phone').text).strip()
            if phone:
                chunks = re.search(
                    '^\(([0-9]{3})\) ([0-9]{3})-([0-9]{4})$',
                    phone
                )
                formatted_phone = chunks.group(1) + "-" + chunks.group(2) + \
                    "-" + chunks.group(3)
                output.append(formatted_phone)
                output_dict['phone'] = formatted_phone
        except:
            pass

        if output:
            info['phoneFacultyExchanges'].add("\n".join(output))
            info['phoneFacultyExchanges_dicts'].append(output_dict)

    info['positionTitle'] = ''
    for vcard in x.findall("individuals/individual/contacts/contact"):
        try:
            if vcard.find('division/name').text != 'Library':
                continue
        except:
            continue

        try:
            title = re.sub('\s+', ' ', vcard.find('title').text).strip()
            if title:
                info['positionTitle'] = title
                break
        except:
            pass

    info['departments'] = set()
    for vcard in x.findall("individuals/individual/contacts/contact"):
        try:
            if vcard.find('division/name').text != 'Library':
                continue
        except:
            continue

        department_name_pieces = []
        try:
            department_name_pieces.append(
                re.sub(
                    '\s+',
                    ' ',
                    vcard.find('department/name').text.strip()
                )
            )
        except:
            pass
        try:
            department_name_pieces.append(
                re.sub(
                    '\s+',
                    ' ',
                    vcard.find('subDepartment/name').text.strip()
                )
            )
        except:
            pass
        info['departments'].add(' - '.join(department_name_pieces))

    return info

def get_all_library_cnetids_from_wagtail():
    output = []
    for s in StaffPage.objects.live():
        try:
            if User.objects.get(username=s.cnetid).is_active:
                output.append(s.cnetid)
        except:
            pass
    return output

def get_individual_info_from_wagtail(cnetid):
    staff_page = StaffPage.objects.get(cnetid=cnetid)

    if staff_page.display_name is None:
        raise ValueError(cnetid + ' has a display_name of None.')

    if staff_page.official_name is None:
        raise ValueError(cnetid + ' has an official_name of None.')

    # officialName is slightly more formal- e.g. "John E. Jung"
    # displayName is a bit more casual- e.g. "John Jung"
    output = {
        "cnetid": cnetid,
        "officialName": staff_page.official_name,
        "displayName": staff_page.display_name,
        "positionTitle": '',
        "email": set(),
        "departments": set(),
        "phoneFacultyExchanges": set()
    }

    for e in staff_page.staff_page_email.all():
        email_str = e.email.strip()
        if email_str:
            output['email'].add(email_str)

    if staff_page.position_title:
        output['positionTitle'] = re.sub(
            '\s+',
            ' ',
            staff_page.position_title
        ).strip()

    for v in staff_page.staff_page_phone_faculty_exchange.all():
        tmp = []

        faculty_exchange = v.faculty_exchange
        if faculty_exchange:
            tmp.append(re.sub('\s+', ' ', faculty_exchange).strip())

        phone_number = v.phone_number
        if phone_number:
            tmp.append(re.sub('\s+', ' ', phone_number).strip())

        if tmp:
            output['phoneFacultyExchanges'].add("\n".join(tmp))

    return output


class WagtailStaffReport:
    """
    Reporting on staff for the HR department. This class includes methods to
    report on the staff that are present in the campus directory but not in
    Wagtail, and it includes general reporting for library staff.
    """

    def __init__(self, sync_report=False, staff_report=False, **options):
        self.sync_report = sync_report
        self.staff_report = staff_report
        self.options = {
            k: options[k] for k in (
                'all',
                'cnetid',
                'department',
                'department_and_subdepartments',
                'group',
                'live',
                'latest_revision_created_at',
                'position_status',
                'supervises_students',
                'supervisor_cnetid',
                'supervisor_override',
                'position_title'
            )
        }

    def _clean(self, string):
        """
        "Clean" a string that came in from the campus directory or from
        Wagtail. Remove leading spaces, replace multiple spaces with a single
        space, etc.
        """
        return re.sub('\s+', ' ', string).strip()

    def workbook(self):
        """
        Returns:
            An OpenPyXL Workbook.
        """
        self.workbook = Workbook()
        self.workbook.remove_sheet(self.workbook.active)
        if self.staff_report:
            self._add_staff_report_worksheet()
        if self.sync_report:
            self._add_staff_out_of_sync_worksheet()
        return self.workbook

    def tab_delimited(self):
        """
        Returns:
            A string. Tab-delimited fields with newlines between records.
        """
        output = ''
        if self.staff_report:
            output = output + self._get_staff_report_tab_delimited()
        if self.staff_report and self.sync_report:
            output = output + "\n\n\n"
        if self.sync_report:
            output = output + self._get_staff_out_of_sync_tab_delimited()
        return output

    def _staff_out_of_sync(self):
        """
        Get lists of staff pages that are out of sync.

        This function returns two lists--first, a list of the names of staff
        pages that are present in Wagtail, but missing in the campus directory.
        Second, a list of the names of staff pages that are present in the
        campus directory but missing in Wagtail.

        Returns: two lists of strings.
        """
        def _format(cnetid, value, field):
            return '{} -{}- ({})'.format(cnetid, self._clean(value), field)

        api_staff_info = set()
        for cnetid in get_all_library_cnetids_from_directory():
            # Don't sync up some staff accounts. Former library directors may
            # appear in the campus directory, but they shouldn't appear in
            # staff listings on the library website. In other cases, staff
            # might have phone numbers connected with non-library jobs. If they
            # want those numbers to appear on the library website, they can add
            # them manually but we won't keep their information in sync. 
            if cnetid in ['judi', 'plb4']:
                continue
            api_staff_info.add(cnetid)
            xml_string = get_xml_from_directory_api(
                'https://directory.uchicago.edu/api/v2/individuals/{}.xml'.format(cnetid)
            )
            info = get_individual_info_from_directory(xml_string)
            api_staff_info.add(
                _format(cnetid, info['officialName'], 'officialName')
            )
            api_staff_info.add(
                _format(cnetid, info['displayName'], 'displayName') 
            )
            api_staff_info.add(
                _format(cnetid, info['positionTitle'], 'positionTitle')
            )
            for email in info['email']:
                api_staff_info.add(
                    _format(cnetid, email, 'email')
                )
            for phone_facex in info['phoneFacultyExchanges']:
                api_staff_info.add(
                    _format(
                        cnetid,
                        re.sub(r"\n", " ", phone_facex),
                        'phoneFacultyExchange'
                    )
                )
            for department in info['departments']:
                api_staff_info.add(
                    _format(cnetid, department, 'department')
                )

        wag_staff_info = set()
        for s in StaffPage.objects.live():
            wag_staff_info.add(s.cnetid)
            wag_staff_info.add(
                _format(s.cnetid, s.official_name, 'officialName')
            )
            wag_staff_info.add(
                _format(s.cnetid, s.display_name, 'displayName')
            )
            wag_staff_info.add(
                _format(s.cnetid, s.position_title, 'positionTitle')
            )
            for e in s.staff_page_email.all():
                wag_staff_info.add(
                    _format(s.cnetid, e.email, 'email')
                )
            for p in s.staff_page_phone_faculty_exchange.all():
                wag_staff_info.add(
                    _format(
                        s.cnetid,
                        '{} {}'.format(
                            p.faculty_exchange,
                            p.phone_number
                        ),
                        'phoneFacultyExchange'
                    )
                )
            for d in s.staff_page_units.all():
                wag_staff_info.add(
                    _format(
                        s.cnetid,
                        d.library_unit.get_campus_directory_full_name(),
                        'department'
                    )
                )

        missing_in_campus_directory = sorted(
            list(wag_staff_info.difference(api_staff_info))
        )
        missing_in_wagtail = sorted(
            list(api_staff_info.difference(wag_staff_info))
        )
        return missing_in_campus_directory, missing_in_wagtail

    def _get_staff_out_of_sync_data(self):
        """
        Get the data for an out of sync staff report, independant of whatever
        format the final report will be in (e.g. Excel or tab-delimited.)
        """
        output = []
        missing_in_campus_directory, missing_in_wagtail = self._staff_out_of_sync()
        if missing_in_campus_directory:
            output.append(["THE FOLLOWING STAFF DATA APPEARS IN WAGTAIL, " +
                           "BUT NOT THE UNIVERSITY'S API:"])
            for c in missing_in_campus_directory:
                output.append([c])
            output.append([""])
        if missing_in_wagtail:
            output.append(["THE FOLLOWING STAFF DATA APPEARS IN THE " +
                           "UNIVERSITY'S API, BUT NOT WAGTAIL:"])
            for w in missing_in_wagtail:
                output.append([w])
            output.append([""])
        return output

    def _add_staff_out_of_sync_worksheet(self):
        """
        Adds a report of the staff that are present in Wagtail but not in the
        campus directory, and vice versa, to a Microsoft Excel spreadsheet.

        Side Effect:
            Adds an OpenPyXL worksheet with information about out of sync
            staff.
        """
        worksheet = self.workbook.create_sheet('out of sync staff')
        for record in self._get_staff_out_of_sync_data():
            worksheet.append(record)

    def _get_staff_out_of_sync_tab_delimited(self):
        """
        Get a report of library staff that are present in Wagtail but not in
        the campus directory, and vice versa.

        Returns:
            A string. Tab delimited data, separated by newlines.
        """
        stringio = io.StringIO()
        writer = csv.writer(
            stringio,
            delimiter='\t',
            quoting=csv.QUOTE_MINIMAL
        )
        for record in self._get_staff_out_of_sync_data():
            writer.writerow(record)
        return stringio.getvalue()

    def _get_staff_wagtail(self):
        """
        Query for a list of UnitPage objects. The options passed to this
        function basically get applied as a Django filter().

        Returns:
            A sorted list of UnitPage objects.
        """
        try:
            if self.options['live']:
                staffpages = set(StaffPage.objects.live())
            else:
                staffpages = set(StaffPage.objects.all())
        except KeyError:
            staffpages = set(StaffPage.objects.all())

        filter_keys = ('cnetid', 'position_title')
        filter_options = {
            k: v for (k, v) in self.options.items() if k in filter_keys and v
        }

        if filter_options:
            new_staffpages = set(StaffPage.objects.filter(**filter_options))
            if staffpages:
                staffpages = staffpages.intersection(new_staffpages)
            else:
                staffpages = new_staffpages

        try:
            if self.options['supervises_students']:
                new_staffpages = set(
                    StaffPage.objects.filter(supervises_students=True)
                )
                if staffpages:
                    staffpages = staffpages.intersection(new_staffpages)
                else:
                    staffpages = new_staffpages
        except KeyError:
            pass

        try:
            if self.options['department']:
                library_units = [
                    u for u in UnitPage.objects.live()
                    if u.get_full_name() == self.options['department']
                ]
                new_staffpages = set(
                    StaffPage.objects.filter(
                        staff_page_units__library_unit__in=library_units
                    )
                )
                if staffpages:
                    staffpages = staffpages.intersection(new_staffpages)
                else:
                    staffpages = new_staffpages
        except KeyError:
            pass

        try:
            if self.options['department_and_subdepartments']:
                library_units = set()
                for u in [
                    u for u in UnitPage.objects.live()
                    if u.get_full_name() ==
                        self.options['department_and_subdepartments']
                ]:
                    library_units = library_units.union(
                        set(u.get_descendants(True).type(UnitPage).specific())
                    )
                new_staffpages = set(
                    StaffPage.objects.filter(
                        staff_page_units__library_unit__in=list(library_units)
                    )
                )
                if staffpages:
                    staffpages = staffpages.intersection(new_staffpages)
                else:
                    staffpages = new_staffpages
        except KeyError:
            pass

        try:
            if self.options['group']:
                new_staffpages = set(
                    StaffPage.objects.filter(
                        member__parent__title=self.options['group']
                    )
                )
                if staffpages:
                    staffpages = staffpages.intersection(new_staffpages)
                else:
                    staffpages = new_staffpages
        except KeyError:
            pass

        try:
            if self.options['latest_revision_created_at']:
                l = '{}-{}-{} 00:00-0600'.format(
                        self.options['latest_revision_created_at'][0:4],
                        self.options['latest_revision_created_at'][4:6],
                        self.options['latest_revision_created_at'][6:8]
                    )
                new_staffpages = set(
                    StaffPage.objects.filter(latest_revision_created_at__gte=l)
                )
                if staffpages:
                    staffpages = staffpages.intersection(new_staffpages)
                else:
                    staffpages = new_staffpages
        except KeyError:
            pass

        try:
            if self.options['position_status']:
                position_status_int = [
                    i for i, v in POSITION_STATUS
                    if v == self.options['position_status']
                ][0]
                new_staffpages = set(
                    StaffPage.objects.filter(position_status=position_status_int)
                )
                if staffpages:
                    staffpages = staffpages.intersection(new_staffpages)
                else:
                    staffpages = new_staffpages
        except KeyError:
            pass

        try:
            if self.options['supervisor_override']:
                new_staffpages = set(
                    StaffPage.objects.exclude(supervisor_override=None)
                )
                if staffpages:
                    staffpages = staffpages.intersection(new_staffpages)
                else:
                    staffpages = new_staffpages
        except KeyError:
            pass

        try:
            if self.options['supervisor_cnetid']:
                new_staffpages = set(
                    StaffPage.objects.get(
                        cnetid=self.options['supervisor_cnetid']
                    ).get_staff()
                )
                if staffpages:
                    staffpages = staffpages.intersection(new_staffpages)
                else:
                    staffpages = new_staffpages
        except KeyError:
            pass

        return sorted(
            list(staffpages),
            key=lambda s: s.last_name if s.last_name else ''
        )

    def _get_staff_report_data(self):
        """
        Get the data for a report of library staff, independant of whatever
        format the final report will be in (e.g. Excel or tab-delimited.)
        """
        output = []
        output.append([
            'ID',
            'LATEST REVISION CREATED AT',
            'NAME AND CNETID',
            'POSITION TITLE',
            'EMAILS',
            'PHONE, FACEX',
            'UNITS (LIBRARY DIRECTORY FULL NAME)',
            'UNITS (CAMPUS DIRECTORY FULL NAME)',
            'GROUPS',
            'EMPLOYEE TYPE',
            'SUPERVISES STUDENTS',
            'POSITION STATUS',
            'SUPERVISOR NAME AND CNETID'
        ])
        staffpages = self._get_staff_wagtail()
        for s in staffpages:
            staffpage_library_units = set(
                StaffPageLibraryUnits.objects.filter(page=s)
            )

            units = []
            for slu in staffpage_library_units:
                units.append(
                    (
                        slu.library_unit.get_full_name(),
                        slu.library_unit.get_campus_directory_full_name()
                    )
                )
            units.sort(key=lambda u: u[0])

            groups = sorted([g.parent.title for g in s.member.all()])

            try:
                latest_revision_created_at = \
                    s.latest_revision_created_at.strftime(
                        '%m/%d/%Y %-I:%M:%S %p'
                    )
            except AttributeError:
                latest_revision_created_at = ''

            name_and_cnetid = '%s (%s)' % (s.title, s.cnetid)

            supervisor_names_and_cnetids = [
                '%s (%s)' % (s.title, s.cnetid) for s in s.get_supervisors
            ]

            emails = [e.email for e in s.staff_page_email.all()]

            phone_facexes = [
                '%s,%s' % (
                    p.faculty_exchange,
                    p.phone_number
                ) for p in s.staff_page_phone_faculty_exchange.all()
            ]

            employee_type_string = [
                v for i, v in EMPLOYEE_TYPES if i == s.employee_type
            ][0]

            position_status_string = [
                v for i, v in POSITION_STATUS if i == s.position_status
            ][0]

            output.append([
                str(s.id),
                latest_revision_created_at,
                name_and_cnetid,
                s.position_title or '',
                '|'.join(emails) or '',
                '|'.join(phone_facexes) or '',
                '|'.join([u[0] for u in units]) or '',
                '|'.join([u[1] for u in units]) or '',
                '|'.join(groups),
                employee_type_string,
                str(s.supervises_students),
                position_status_string,
                '|'.join(supervisor_names_and_cnetids)
            ])
        return output

    def _add_staff_report_worksheet(self):
        """
        Add a report of library staff in Microsoft Excel format, for HR
        reporting.

        Side Effect:
            Adds an OpenPyXL worksheet with information about staff.
        """
        worksheet = self.workbook.create_sheet(title='wagtail staff')
        for record in self._get_staff_report_data():
            worksheet.append(record)

    def _get_staff_report_tab_delimited(self):
        """
        Get a report of library staff in tab delimited format, for HR
        reporting.

        Returns:
            A string. Tab delimited data, separated by newlines.
        """
        stringio = io.StringIO()
        writer = csv.writer(
            stringio,
            delimiter='\t',
            quoting=csv.QUOTE_MINIMAL
        )
        for record in self._get_staff_report_data():
            writer.writerow(record)
        return stringio.getvalue()
