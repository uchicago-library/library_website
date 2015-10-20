# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0007_auto_20151020_1708'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unitpagephonenumbers',
            name='number',
            field=models.CharField(max_length=12, validators=[django.core.validators.RegexValidator(message='Please enter the phone number using the format 773-123-4567', regex='^[0-9]{3}-[0-9]{3}-[0-9]{4}$')]),
        ),
    ]
