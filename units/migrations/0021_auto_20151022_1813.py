# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0020_auto_20151022_1746'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='unitpagefaxnumbers',
            name='page',
        ),
        migrations.AddField(
            model_name='unitpage',
            name='fax_number',
            field=models.CharField(validators=[django.core.validators.RegexValidator(message='Please enter the phone number using the format 773-123-4567', regex='^[0-9]{3}-[0-9]{3}-[0-9]{4}$')], blank=True, max_length=12),
        ),
        migrations.DeleteModel(
            name='UnitPageFaxNumbers',
        ),
    ]
