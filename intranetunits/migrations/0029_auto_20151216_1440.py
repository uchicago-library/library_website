# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import modelcluster.fields
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtaildocs', '0003_add_verbose_names'),
        ('intranetunits', '0028_auto_20151215_1845'),
    ]

    operations = [
        migrations.CreateModel(
            name='IntranetUnitsReportsPageTable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('date', models.DateField()),
                ('summary', models.TextField()),
                ('link', models.URLField(blank=True, max_length=254, default='')),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='wagtaildocs.Document', related_name='+', null=True, blank=True)),
                ('page', modelcluster.fields.ParentalKey(to='intranetunits.IntranetUnitsPage', related_name='intranet_units_reports')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='intranetunitreportspagetable',
            name='document',
        ),
        migrations.RemoveField(
            model_name='intranetunitreportspagetable',
            name='page',
        ),
        migrations.DeleteModel(
            name='IntranetUnitReportsPageTable',
        ),
    ]
