# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0008_image_created_at_index'),
        ('staff', '0000_manual_pre_initial'),
        ('units', '0000_manual_pre_initial'),
        ('wagtailcore', '0020_add_index_on_page_first_published_at'),
        ('public', '0011_auto_20151119_2133'),
    ]

    operations = [
        migrations.CreateModel(
            name='FloorPlanPage',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, to='wagtailcore.Page', primary_key=True, serialize=False, auto_created=True)),
                ('last_reviewed', models.DateField(blank=True, null=True, verbose_name='Last Reviewed')),
                ('sort_order', models.IntegerField(blank=True, default=0)),
                ('content_specialist', models.ForeignKey(related_name='public_floorplanpage_content_specialist', to='staff.StaffPage', on_delete=django.db.models.deletion.SET_NULL, null=True)),
                ('editor', models.ForeignKey(related_name='public_floorplanpage_editor', to='staff.StaffPage', on_delete=django.db.models.deletion.SET_NULL, null=True)),
                ('image', models.ForeignKey(blank=True, null=True, to='wagtailimages.Image', on_delete=django.db.models.deletion.SET_NULL, related_name='+')),
                ('page_maintainer', models.ForeignKey(related_name='public_floorplanpage_maintainer', to='staff.StaffPage', on_delete=django.db.models.deletion.SET_NULL, null=True)),
                ('unit', models.ForeignKey(blank=True, null=True, to='units.UnitPage', on_delete=django.db.models.deletion.SET_NULL, related_name='public_floorplanpage_related')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]
