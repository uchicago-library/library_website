# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0009_auto_20151020_1722'),
    ]

    operations = [
        migrations.CreateModel(
            name='UnitPageFaxNumbers',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('sort_order', models.IntegerField(null=True, editable=False, blank=True)),
                ('label', models.CharField(max_length=25)),
                ('number', models.CharField(validators=[django.core.validators.RegexValidator(message='Please enter the phone number using the format 773-123-4567', regex='^[0-9]{3}-[0-9]{3}-[0-9]{4}$')], max_length=12)),
                ('page', modelcluster.fields.ParentalKey(related_name='fax_numbers', to='units.UnitPage')),
            ],
            options={
                'abstract': False,
                'ordering': ['sort_order'],
            },
        ),
    ]
