# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0031_auto_20151022_1633'),
    ]

    operations = [
        migrations.AddField(
            model_name='locationpage',
            name='label',
            field=models.CharField(max_length=25, default='Phone Number'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='locationpage',
            name='number',
            field=models.CharField(max_length=12, default='773-702-4391', validators=[django.core.validators.RegexValidator(regex='^[0-9]{3}-[0-9]{3}-[0-9]{4}$', message='Please enter the phone number using the format 773-123-4567')]),
            preserve_default=False,
        ),
    ]
