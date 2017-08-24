from django.conf.urls import url
from django.core import management
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render
from openpyxl.writer.excel import save_virtual_workbook
from wagtail.wagtailadmin.menu import MenuItem
from wagtail.wagtailcore import hooks

from .forms import StaffReportingForm
from .utils import report_staff_wagtail

def admin_view(request):
    if request.method == 'POST':
        form = StaffReportingForm(request.POST)
        options = {
            'filename': form.data.get('filename', None),
            'all': False,
            'cnetid': form.data.get('cnetid', None),
            'department': form.data.get('department', None),
            'department_and_subdepartments': form.data.get('department_and_subdepartments', None),
            'live': False,
            'modified_since': form.data.get('modified_since', None),
            'position_status': form.data.get('position_status', None),
            'supervises_students': form.data.get('supervises_students', None),
            'supervisor_cnetid': form.data.get('supervisor_cnetid', None),
            'supervisor_override_set': form.data.get('supervisor_override_set', None),
            'title': form.data.get('title', None)
        }
        if form.data.get('all_or_live') == 'all':
            options['all'] = True
        elif form.data.get('all_or_live') == 'live':
            options['live'] = True
        if form.is_valid():
            workbook = report_staff_wagtail(**options)
            virtual_workbook = save_virtual_workbook(workbook)
            response = HttpResponse(virtual_workbook, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['content-disposition'] = 'attachment; filename="' + options['filename'] + '.xlsx"'
            return response
        else:
            return render(request, 'staff/staff_reporting_form.html', {'form': form})
    else:
        form = StaffReportingForm({'all_or_live': 'live'})
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
  return MenuItem('Staff Reporting', reverse('list_staff_wagtail'), classnames='icon icon-mail', order=9999)
