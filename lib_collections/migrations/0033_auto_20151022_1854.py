# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0019_verbose_names_cleanup'),
        ('staff', '0004_auto_20151020_1954'),
        ('units', '0023_auto_20151022_1854'),
        ('lib_collections', '0032_collectionpage_page_maintainer'),
    ]

    operations = [
        migrations.CreateModel(
            name='CollectingAreaPage',
            fields=[
                ('page_ptr', models.OneToOneField(to='wagtailcore.Page', auto_created=True, primary_key=True, parent_link=True, serialize=False)),
                ('description', models.TextField(blank=True)),
                ('last_reviewed', models.DateTimeField(null=True, blank=True, verbose_name='Last Reviewed')),
                ('collecting_statement', models.TextField()),
                ('page_maintainer', models.ForeignKey(related_name='lib_collections_collectingareapage_related_maintainer', on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True, blank=True)),
                ('subject_specialist', models.ForeignKey(related_name='lib_collections_collectingareapage_related', on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True)),
                ('unit', models.ForeignKey(related_name='lib_collections_collectingareapage_related', on_delete=django.db.models.deletion.SET_NULL, to='units.UnitPage', null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.AlterField(
            model_name='collectionpage',
            name='page_maintainer',
            field=models.ForeignKey(related_name='lib_collections_collectionpage_related_maintainer', on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True, blank=True),
        ),
    ]
