# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0019_unitpage_page_maintainer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unitpagephonenumbers',
            name='label',
            field=models.CharField(max_length=25, blank=True),
        ),
        migrations.AlterField(
            model_name='unitpagephonenumbers',
            name='number',
            field=models.CharField(validators=[django.core.validators.RegexValidator(regex='^[0-9]{3}-[0-9]{3}-[0-9]{4}$', message='Please enter the phone number using the format 773-123-4567')], max_length=12, blank=True),
        ),
    ]
