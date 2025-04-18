# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-12 19:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0045_auto_20160610_1600'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newspage',
            name='excerpt',
            field=wagtail.fields.RichTextField(blank=True, help_text='Shown on the News feed. Populated automatically from “Body” if left empty.', null=True),
        ),
        migrations.AlterField(
            model_name='newspage',
            name='sticky_until',
            field=models.DateField(blank=True, help_text='To be used by Admin and HR only.', null=True),
        ),
        migrations.AlterField(
            model_name='newspage',
            name='story_date',
            field=models.DateField(default=django.utils.timezone.now, help_text='If you use Settings to publish a future post, put the publish date here. Otherwise, leave today as the story date.'),
        ),
    ]
