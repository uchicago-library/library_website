# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0026_remove_unitpage_description'),
        ('staff', '0009_remove_staffpage_is_subject_specialist'),
    ]

    operations = [
        migrations.CreateModel(
            name='VCard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('phone_label', models.CharField(blank=True, max_length=25)),
                ('phone_number', models.CharField(blank=True, validators=[django.core.validators.RegexValidator(message='Please enter the phone number using the format 773-123-4567', regex='^[0-9]{3}-[0-9]{3}-[0-9]{4}$')], max_length=12)),
                ('title', models.CharField(max_length=255)),
                ('faculty_exchange', models.CharField(max_length=255)),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, null=True, blank=True, related_name='staff_vcard_related', to='units.UnitPage')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='stafftitle',
            name='staff',
        ),
        migrations.DeleteModel(
            name='StaffTitle',
        ),
    ]
