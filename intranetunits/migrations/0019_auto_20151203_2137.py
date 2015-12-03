# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('intranetunits', '0018_auto_20151203_1806'),
    ]

    operations = [
        migrations.AddField(
            model_name='intranetunitspage',
            name='internal_email',
            field=models.EmailField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='intranetunitspage',
            name='internal_location',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='intranetunitspage',
            name='internal_phone_number',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
