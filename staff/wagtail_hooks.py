from django.conf.urls import url
from django.core import management
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render
from openpyxl.writer.excel import save_virtual_workbook
from wagtail.wagtailadmin.menu import MenuItem
from wagtail.wagtailcore import hooks

from .utils import report_staff_wagtail

def admin_view(request):
    # Needs to be inside for unit tests
    from .forms import StaffReportingForm
    if request.method == 'POST':
        form = StaffReportingForm(request.POST)
        options = {
            'filename': form.data.get('filename', 'staff_report'),
            'cnetid': form.data.get('cnetid', None),
            'department': form.data.get('department', None),
            'department_and_subdepartments': form.data.get('department_and_subdepartments', None),
            'live': form.data.get('live', None),
            'latest_revision_created_at': form.data.get('latest_revision_created_at', None),
            'position_status': form.data.get('position_status', None),
            'supervises_students': form.data.get('supervises_students', False),
            'supervisor_cnetid': form.data.get('supervisor_cnetid', None),
            'supervisor_override': form.data.get('supervisor_override', None),
            'position_title': form.data.get('position_title', None)
        }

        for i in ('live', 'supervises_students', 'supervisor_override'):
            try:
                if options[i]:
                    options[i] = True
            except KeyError:
                continue

        if form.is_valid():
            workbook = report_staff_wagtail(**options)
            virtual_workbook = save_virtual_workbook(workbook)
            response = HttpResponse(virtual_workbook, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['content-disposition'] = 'attachment; filename="' + options['filename'] + '.xlsx"'
            return response
        else:
            return render(request, 'staff/staff_reporting_form.html', {'form': form})
    else:
        form = StaffReportingForm({'live': True, 'filename': 'staff_report'})
    return render(request, 'staff/staff_reporting_form.html', {
        'form': form
    })

@hooks.register('register_admin_urls')
def urlconf_time():
    return [
        url(r'^list_staff_wagtail/$', admin_view, name='list_staff_wagtail')
    ]

@hooks.register('register_settings_menu_item')
def register_frank_menu_item():
  return MenuItem('Staff Reporting', reverse('list_staff_wagtail'), classnames='icon icon-mail', order=9990)
