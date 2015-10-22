# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0030_auto_20151022_1614'),
    ]

    operations = [
        migrations.AlterField(
            model_name='locationpage',
            name='postal_code',
            field=models.CharField(validators=[django.core.validators.RegexValidator(message='Please enter the postal code as a five digit number, e.g. 60637', regex='^[0-9]{5}$')], blank=True, max_length=5),
        ),
    ]
