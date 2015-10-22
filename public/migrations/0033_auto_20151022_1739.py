# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import modelcluster.fields
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0032_auto_20151022_1729'),
    ]

    operations = [
        migrations.CreateModel(
            name='LocationPagePhoneNumbers',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('sort_order', models.IntegerField(editable=False, blank=True, null=True)),
                ('label', models.CharField(max_length=25)),
                ('number', models.CharField(validators=[django.core.validators.RegexValidator(message='Please enter the phone number using the format 773-123-4567', regex='^[0-9]{3}-[0-9]{3}-[0-9]{4}$')], max_length=12)),
            ],
            options={
                'abstract': False,
                'ordering': ['sort_order'],
            },
        ),
        migrations.RemoveField(
            model_name='locationpage',
            name='label',
        ),
        migrations.RemoveField(
            model_name='locationpage',
            name='number',
        ),
        migrations.AddField(
            model_name='locationpagephonenumbers',
            name='page',
            field=modelcluster.fields.ParentalKey(to='public.LocationPage', related_name='phone_numbers'),
        ),
    ]
