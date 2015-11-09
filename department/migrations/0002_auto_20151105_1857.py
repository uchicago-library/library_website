# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('department', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='departmentpage',
            name='name',
        ),
        migrations.AddField(
            model_name='departmentpage',
            name='body',
            field=wagtail.wagtailcore.fields.RichTextField(default='body'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='departmentpage',
            name='location',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name='departmentpage',
            name='telephone',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AlterField(
            model_name='departmentindexpage',
            name='intro',
            field=wagtail.wagtailcore.fields.RichTextField(),
        ),
    ]
