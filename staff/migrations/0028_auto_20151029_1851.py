# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0026_remove_unitpage_description'),
        ('staff', '0027_auto_20151029_1850'),
    ]

    operations = [
        migrations.CreateModel(
            name='VCard',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('phone_label', models.CharField(blank=True, max_length=25)),
                ('phone_number', models.CharField(blank=True, validators=[django.core.validators.RegexValidator(regex='^[0-9]{3}-[0-9]{3}-[0-9]{4}$', message='Please enter the phone number using the format 773-123-4567')], max_length=12)),
                ('title', models.CharField(max_length=255)),
                ('faculty_exchange', models.CharField(blank=True, max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='StaffPagePageVCards',
            fields=[
                ('vcard_ptr', models.OneToOneField(parent_link=True, to='staff.VCard', serialize=False, primary_key=True, auto_created=True)),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('page', modelcluster.fields.ParentalKey(to='staff.StaffPage', related_name='vcards')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
            bases=('staff.vcard', models.Model),
        ),
        migrations.AddField(
            model_name='vcard',
            name='unit',
            field=models.ForeignKey(null=True, blank=True, related_name='staff_vcard_related', on_delete=django.db.models.deletion.SET_NULL, to='units.UnitPage'),
        ),
    ]
