# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate

from django.core.management.base import BaseCommand

from base.utils import save_virtual_workbook
from units.utils import WagtailUnitsReport


class Command(BaseCommand):
    """
    Produce reports of units in Wagtail. We should be able to run this in the
    shell and produce text output or use this in cron to send Excel
    spreadsheets to HR via email.
    """

    def add_arguments(self, parser):
        parser.add_argument("--all", action="store_true", default=False)
        parser.add_argument("--live", action="store_true", default=False)
        parser.add_argument("--latest-revision-created-at", type=str)
        parser.add_argument(
            "--display-in-campus-directory", action="store_true", default=False
        )
        parser.add_argument(
            "--report-out-of-sync-units", action="store_true", default=False
        )
        parser.add_argument(
            "--report-out-of-sync-intranet-units", action="store_true", default=False
        )
        parser.add_argument(
            "--output-format", choices=("excel", "text"), default="text", type=str
        )
        parser.add_argument("--filename", type=str, default="")
        parser.add_argument("--email-from", type=str, default="")
        parser.add_argument("--email-to", type=str, default="")

    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement this
        method. It may return a Unicode string which will be printed to
        stdout. More: https://docs.djangoproject.com/en/1.8/howto/custom
        -management-commands/#django.core.management.BaseCommand.handle
        """

        units_report = WagtailUnitsReport(
            sync_report=options["report_out_of_sync_units"],
            intranet_sync_report=options["report_out_of_sync_intranet_units"],
            unit_report=options["all"] or options["live"],
            **options,
        )

        if options["output_format"] == "excel":
            if options["email_to"]:
                virtual_workbook = save_virtual_workbook(units_report.workbook())

                msg = MIMEMultipart()
                msg["Subject"] = "Wagtail Units Report"
                msg["From"] = "jej@uchicago.edu"
                msg["To"] = options["email_to"]
                msg["Date"] = formatdate(localtime=True)

                attachment = MIMEApplication(virtual_workbook, Name=options["filename"])
                attachment["Content-Disposition"] = 'attachment; filename="{}"'.format(
                    options["filename"]
                )
                msg.attach(attachment)
                s = smtplib.SMTP("localhost")
                s.send_message(msg)
                s.quit()
            elif options["filename"]:
                units_report.workbook().save(options["filename"])
        elif options["output_format"] == "text":
            return units_report.tab_delimited()
