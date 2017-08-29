from django.conf.urls import url
from django.core import management
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render
from openpyxl.writer.excel import save_virtual_workbook
from wagtail.wagtailadmin.menu import MenuItem
from wagtail.wagtailcore import hooks

from .forms import UnitReportingForm
from .utils import report_units_wagtail

def admin_view(request):
    if request.method == 'POST':
        form = UnitReportingForm(request.POST)
        options = {
            'filename': form.data.get('filename', 'unit_report'),
            'live': form.data.get('live', None),
            'latest_revision_created_at': form.data.get('latest_revision_created_at', None),
        }
        if form.is_valid():
            workbook = report_units_wagtail(**options)
            virtual_workbook = save_virtual_workbook(workbook)
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

@hooks.register('register_admin_urls')
def urlconf_time():
    return [
        url(r'^list_units_wagtail/$', admin_view, name='list_units_wagtail')
    ]

@hooks.register('register_settings_menu_item')
def register_frank_menu_item():
  return MenuItem('Unit Reporting', reverse('list_units_wagtail'), classnames='icon icon-mail', order=9999)
