# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0022_auto_20151029_1826'),
    ]

    operations = [
        migrations.AddField(
            model_name='staffpagepagevcards',
            name='phone_label',
            field=models.CharField(blank=True, max_length=25),
        ),
        migrations.AddField(
            model_name='staffpagepagevcards',
            name='phone_number',
            field=models.CharField(blank=True, validators=[django.core.validators.RegexValidator(regex='^[0-9]{3}-[0-9]{3}-[0-9]{4}$', message='Please enter the phone number using the format 773-123-4567')], max_length=12),
        ),
    ]
