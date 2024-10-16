# Generated by Django 3.2.15 on 2023-06-01 18:24

import base.models
from django.db import migrations
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('lib_news', '0020_auto_20220920_1154'),
    ]

    operations = [
        migrations.AddField(
            model_name='libnewsindexpage',
            name='link_queue',
            field=wagtail.fields.StreamField([('spreadsheet', base.models.LinkQueueSpreadsheetBlock())], blank=True, default='', help_text='Spreadsheets should be .xlsx files with the following headers: "Start Date", "End Date", "Link Text", and "URL"', use_json_field=True),
        ),
        migrations.AddField(
            model_name='libnewspage',
            name='link_queue',
            field=wagtail.fields.StreamField([('spreadsheet', base.models.LinkQueueSpreadsheetBlock())], blank=True, default='', help_text='Spreadsheets should be .xlsx files with the following headers: "Start Date", "End Date", "Link Text", and "URL"', use_json_field=True),
        ),
    ]
