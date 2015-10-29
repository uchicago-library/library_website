# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0014_auto_20151029_1807'),
    ]

    operations = [
        migrations.AddField(
            model_name='vcard',
            name='phone_label',
            field=models.CharField(max_length=25, blank=True),
        ),
        migrations.AddField(
            model_name='vcard',
            name='phone_number',
            field=models.CharField(max_length=12, validators=[django.core.validators.RegexValidator(message='Please enter the phone number using the format 773-123-4567', regex='^[0-9]{3}-[0-9]{3}-[0-9]{4}$')], blank=True),
        ),
    ]
