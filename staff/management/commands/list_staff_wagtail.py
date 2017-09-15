# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from staff.models import POSITION_STATUS
from staff.utils import WagtailStaffReport

class Command (BaseCommand):
    """
    Produce reports of staff in Wagtail that can be imported into Excel. 
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            default=False,
            action='store_true'
        )
        parser.add_argument(
            '--cnetid',
            type=str,
            action='store'
        )
        parser.add_argument(
            '--department',
            type=str,
            action='store'
        )
        parser.add_argument(
            '--department-and-subdepartments',
            type=str,
            action='store'
        )
        parser.add_argument(
            '--live',
            default=False,
            action='store_true'
        )
        parser.add_argument(
            '--latest-revision-created-at',
            type=str,
            action='store'
        )
        parser.add_argument(
            '--position-status',
            type=str,
            action='store',
            choices=[status[1] for status in POSITION_STATUS]
        )
        parser.add_argument(
            '--supervises-students',
            default=False,
            action='store_true'
        )
        parser.add_argument(
            '--supervisor-cnetid',
            type=str,
            action='store'
        )
        parser.add_argument(
            '--supervisor-override',
            default=False,
            action='store_true'
        )
        parser.add_argument(
            '--position-title',
            type=str,
            action='store'
        )
        parser.add_argument(
            '--report-out-of-sync-staff',
            default=False,
            action='store_true'
        )
        parser.add_argument(
            '--output-format',
            choices=('excel', 'text'),
            default='text',
            type=str
        )
        parser.add_argument(
            '--filename',
            default='',
            type=str
        )
        parser.add_argument(
            '--email-from',
            type=str,
            default=''
        )
        parser.add_argument(
            '--email-to',
            type=str,
            default=''
        )

    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement this 
        method. It may return a Unicode string which will be printed to 
        stdout. More: https://docs.djangoproject.com/en/1.8/howto/custom
        -management-commands/#django.core.management.BaseCommand.handle
        """
        staff_report = any((bool(options['all']),
                            bool(options['cnetid']),
                            bool(options['department']),
                            bool(options['department_and_subdepartments']),
                            bool(options['live']),
                            bool(options['latest_revision_created_at']),
                            bool(options['position_status']),
                            bool(options['supervises_students']),
                            bool(options['supervisor_cnetid']),
                            bool(options['supervisor_override']),
                            bool(options['position_title'])))

        staff_report = WagtailStaffReport(
            sync_report = options['report_out_of_sync_staff'],
            staff_report = staff_report,
            **options
        )

        if options['output_format'] == 'excel':
            if options['email_to']:        
                msg = MIMEMultipart()
                msg['Subject'] = 'Wagtail Staff Report'
                msg['From'] = 'jej@uchicago.edu'
                msg['To'] = options['email-to']
                msg['Date'] = formatdate(localtime=True)

                attachment = MIMEApplication(
                    staff.workbook(),
                    Name='staffreport.xlsx'
                )
                attachment['Content-Disposition'] = 'attachment; filename="staffreport.xlsx"'
                ms.attach(attachment)
                s = smtplib.SMTP('localhost')
                s.send_message(msg)
                s.quit()
            elif options['filename']:
                staff_report.workbook().save(options['filename'])
        elif options['output_format'] == 'text':
            return staff_report.tab_delimited()
