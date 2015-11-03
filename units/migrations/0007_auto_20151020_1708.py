# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0006_auto_20151020_1657'),
    ]

    operations = [
        migrations.RenameField(
            model_name='unitpagephonenumbers',
            old_name='phone_label',
            new_name='label',
        ),
        migrations.RemoveField(
            model_name='unitpagephonenumbers',
            name='phone_number',
        ),
        migrations.AddField(
            model_name='unitpagephonenumbers',
            name='number',
            field=models.CharField(blank=True, validators=[django.core.validators.RegexValidator(message='Please enter the phone number using the format 773-123-4567', regex='^[0-9]{3}-[0-9]{3}-[0-9]{4}$')], max_length=12),
        ),
    ]
