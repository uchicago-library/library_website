# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0003_auto_20151008_1530'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staffpage',
            name='cnetid',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='staffpage',
            name='display_name',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='staffpage',
            name='email',
            field=models.CharField(validators=[django.core.validators.EmailValidator()], max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='staffpage',
            name='official_name',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
