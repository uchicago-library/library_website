from .models import Tree
from .forms import UnitReportingForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.db.models.expressions import RawSQL
from django.http import HttpResponse
from django.shortcuts import render
from openpyxl.writer.excel import save_virtual_workbook
from staff.models import StaffPage, StaffPageSubjectPlacement
from subjects.models import Subject
from units.models import UnitIndexPage, UnitPage
from units.utils import get_quick_nums_for_library_or_dept
from units.utils import WagtailUnitsReport
from wagtail.wagtailimages.models import Image
from public.models import StandardPage, LocationPage
from library_website.settings import PUBLIC_HOMEPAGE, QUICK_NUMS, REGENSTEIN_HOMEPAGE, SSA_HOMEPAGE, MANSUETO_HOMEPAGE, CRERAR_HOMEPAGE, ECKHART_HOMEPAGE, DANGELO_HOMEPAGE, SCRC_HOMEPAGE
from base.utils import get_hours_and_location, get_page_loc_name
from ask_a_librarian.utils import get_chat_status, get_chat_status_css, get_unit_chat_link
from django.utils.text import slugify

import os
import re
import subprocess
import urllib.parse

def get_staff_pages_for_library(library = None):
    all_staff = StaffPage.objects.live().order_by('last_name', 'first_name')
    if library:
        # see units.models.BUILDINGS
        library_name_to_building = {
            get_page_loc_name(ECKHART_HOMEPAGE): 3,
            get_page_loc_name(CRERAR_HOMEPAGE): 1,
            get_page_loc_name(DANGELO_HOMEPAGE): 2,
            get_page_loc_name(SSA_HOMEPAGE): 7,
            LocationPage.objects.live().get(id=REGENSTEIN_HOMEPAGE).title: 5,
            get_page_loc_name(SCRC_HOMEPAGE): 6,
            get_page_loc_name(MANSUETO_HOMEPAGE): 4
        }
        try:
            building = library_name_to_building[library]
            return StaffPage.objects.filter(staff_page_units__library_unit__building=building).distinct().order_by('last_name', 'first_name')
        except:
            return all_staff 
    else:
        return all_staff

def get_staff_pages_for_unit(unit_page_full_name = None, recursive = False, display_supervisor_first = False):
    unit_page_ids = None
    unit_page = None
    if unit_page_full_name:
        for u in UnitPage.objects.live():
            if u.get_full_name() == unit_page_full_name:
                unit_page = u
                if recursive:
                    unit_page_ids = list(u.get_descendants(True).values_list('id', flat=True))
                else:
                    unit_page_ids = [u.id]
                break

    if unit_page_ids == None:
        recursive = True
        unit_page_ids = list(UnitIndexPage.objects.first().get_descendants(True).values_list('id', flat=True))
 
    staff_pages = StaffPage.objects.live().filter(staff_page_units__library_unit__id__in=unit_page_ids).distinct().order_by('last_name', 'first_name')
    
    if display_supervisor_first:
        if unit_page and unit_page.department_head:
            staff_pages = [unit_page.department_head] + list(staff_pages.exclude(id=unit_page.department_head.id))
        
    return staff_pages

def get_libraries():
    return sorted(
        [str(p) for p in LocationPage.objects.live().filter(is_building=True)],
        key=lambda p: re.sub(r'^The ', '', p)
    )

def units(request):
    divisions = []
    
    department = request.GET.get('department', None)
    library = request.GET.get('library', None)
    page = request.GET.get('page', 1)
    query = request.GET.get('query', None)
    subject = request.GET.get('subject', None)
    view = request.GET.get('view', 'staff')

    if library == 'The University of Chicago Library':
        library = None

    if query:
        view = None

    staff_pages = []
    departments = []

    if query:
      staff_pages = StaffPage.objects.live().search(query)
      departments = UnitPage.objects.filter(display_in_library_directory=True, live=True).search(query)

    elif view == 'staff':
        # returns all staff pages if library is None.
        # otherwise, returns staff pages for the given library.
        staff_pages = get_staff_pages_for_library(library)

        # departments.
        if department:
            staff_pages = get_staff_pages_for_unit(department, True, True)

        # subjects.
        if subject:
            if subject == 'All Subject Specialists':
                staff_pages = staff_pages.filter(id__in=StaffPageSubjectPlacement.objects.all().values_list('page', flat=True).distinct())
            else:
                # get a subject and all it's descendants. 
                subject_and_descendants = Subject.objects.get(name=subject).get_descendants()
                # from staff page subject placements, get all of the staff that match those subjects. 
                subject_staff_ids = StaffPageSubjectPlacement.objects.filter(subject__in=subject_and_descendants).values_list('page', flat=True)
                # filter staff_pages to only include those staff pages. 
                staff_pages = staff_pages.filter(id__in=subject_staff_ids).order_by('last_name')

    elif view == 'department':
      divisions = []
      for division in UnitIndexPage.objects.first().get_children().specific().type(UnitPage).filter(live=True, unitpage__display_in_library_directory=True).order_by('title'):
        divisions.append({
          'unit': division,
          'descendants': division.get_descendants().specific().type(UnitPage).filter(live=True, unitpage__display_in_library_directory=True).order_by('title')
        })
    
    default_image = Image.objects.get(title="Default Placeholder Photo")

    try:
        org_chart_image = Image.objects.get(title="Org Chart")
    except:
        org_chart_image = None

    # Page context variables for templates
    home_page = StandardPage.objects.live().get(id=PUBLIC_HOMEPAGE)
    location_and_hours = get_hours_and_location(home_page)
    location = str(location_and_hours['page_location'])
    unit = location_and_hours['page_unit']

    title = ''
    if query:
      title = 'Search Results'
    elif view == 'staff':
      title = 'Library Directory: Staff'
    elif view == 'department': 
      title = 'Library Directory: Departments'
    elif view == 'org':
      title = 'Library Directory: Org Chart'

    quick_nums = get_quick_nums_for_library_or_dept(request).replace('<td>', '<li>').replace('</td>', '</li>')

    return render(request, 'units/unit_index_page.html', {
        'breadcrumb_div_css': 'col-md-12 breadcrumbs hidden-xs hidden-sm',
        'content_div_css': 'container body-container directory col-xs-12 col-lg-11 col-lg-offset-1',
        'department': department,
        'departments': departments,
        'default_image': default_image,
        'divisions': divisions,
        'libraries': get_libraries(),
        'library': library,
        'org_chart_image': org_chart_image,
        'query': query,
        'staff_pages': staff_pages,
        'subjects': Subject.objects.filter(display_in_dropdown=True).values_list('name', flat=True),
        'subject': subject,
        'view': view,
        'self': {
            'title': title
        },
        'page_unit': str(unit),
        'page_location': location,
        'address': location_and_hours['address'],
        'chat_url': get_unit_chat_link(unit, request),
        'chat_status': get_chat_status('uofc-ask'),
        'chat_status_css': get_chat_status_css('uofc-ask'),
        'hours_page_url': home_page.get_hours_page(request),
        'quick_nums': quick_nums
    })

def unit_reporting_admin_view(request):
    """
    Provide a form in the Wagtail admin for HR to get reports on Library units.
    """
    if request.method == 'POST':
        form = UnitReportingForm(request.POST)
        options = {
            'display_in_campus_directory': form.data.get('display_in_campus_directory', False),
            'email_to': form.data.get('email_to', None),
            'filename': form.data.get('filename', 'unit_report'),
            'live': form.data.get('live', None),
            'latest_revision_created_at': form.data.get('latest_revision_created_at', None),
        }
        options['all'] = not(bool(options['live']))
        if form.is_valid():
            unit_report = WagtailUnitsReport(
                sync_report = False,
                unit_report = True,
                **options
            )
            virtual_workbook = save_virtual_workbook(unit_report.workbook())
            response = HttpResponse(virtual_workbook, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['content-disposition'] = 'attachment; filename="' + options['filename'] + '.xlsx"'
            return response
        else:
            return render(request, 'units/unit_reporting_form.html', {'form': form})
    else:
        form = UnitReportingForm({'live': True, 'filename': 'unit_report'})
    return render(request, 'units/unit_reporting_form.html', {
        'form': form
    })

