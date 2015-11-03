# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0004_auto_20151020_1548'),
    ]

    operations = [
        migrations.CreateModel(
            name='UnitPagePhoneNumbers',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('phone_label', models.CharField(max_length=25)),
                ('phone_number', models.CharField(validators=[django.core.validators.RegexValidator(message='Please enter the phone number using the format 000-123-4567', regex='^[0-9]{3}-[0-9]{3}-[0-9]{4}$')], blank=True, max_length=10)),
                ('page', modelcluster.fields.ParentalKey(related_name='phone_numbers', to='units.UnitPage')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
    ]
