# Generated by Django 3.2.15 on 2023-06-01 18:24

import base.models
from django.db import migrations
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ask_a_librarian', '0022_auto_20220920_1154'),
    ]

    operations = [
        migrations.AddField(
            model_name='askpage',
            name='link_queue',
            field=wagtail.fields.StreamField([('spreadsheet', base.models.LinkQueueSpreadsheetBlock())], blank=True, default='', help_text='Spreadsheets should be .xlsx files with the following headers: "Start Date", "End Date", "Link Text", and "URL"', use_json_field=True),
        ),
    ]