# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0002_auto_20151113_2245'),
        ('units', '0001_initial'),
        ('staff', '0001_initial'),
        ('wagtailimages', '0008_image_created_at_index'),
    ]

    operations = [
        migrations.AddField(
            model_name='standardpage',
            name='unit',
            field=models.ForeignKey(to='units.UnitPage', on_delete=django.db.models.deletion.SET_NULL, related_name='public_standardpage_related', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='locationpagedonorplacement',
            name='donor',
            field=models.ForeignKey(to='public.DonorPage', on_delete=django.db.models.deletion.SET_NULL, related_name='location_donor_page', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='locationpagedonorplacement',
            name='parent',
            field=modelcluster.fields.ParentalKey(to='public.LocationPage', related_name='location_donor_page_placements', on_delete=django.db.models.deletion.SET_NULL, null=True),
        ),
        migrations.AddField(
            model_name='locationpage',
            name='content_specialist',
            field=models.ForeignKey(to='staff.StaffPage', related_name='public_locationpage_content_specialist', on_delete=django.db.models.deletion.SET_NULL, null=True),
        ),
        migrations.AddField(
            model_name='locationpage',
            name='editor',
            field=models.ForeignKey(to='staff.StaffPage', related_name='public_locationpage_editor', on_delete=django.db.models.deletion.SET_NULL, null=True),
        ),
        migrations.AddField(
            model_name='locationpage',
            name='location_photo',
            field=models.ForeignKey(to='wagtailimages.Image', on_delete=django.db.models.deletion.SET_NULL, related_name='+', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='locationpage',
            name='page_maintainer',
            field=models.ForeignKey(to='staff.StaffPage', related_name='public_locationpage_maintainer', on_delete=django.db.models.deletion.SET_NULL, null=True),
        ),
        migrations.AddField(
            model_name='locationpage',
            name='parent_building',
            field=models.ForeignKey(to='public.LocationPage', on_delete=django.db.models.deletion.SET_NULL, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='locationpage',
            name='unit',
            field=models.ForeignKey(to='units.UnitPage', on_delete=django.db.models.deletion.SET_NULL, related_name='public_locationpage_related', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='donorpage',
            name='content_specialist',
            field=models.ForeignKey(to='staff.StaffPage', related_name='public_donorpage_content_specialist', on_delete=django.db.models.deletion.SET_NULL, null=True),
        ),
        migrations.AddField(
            model_name='donorpage',
            name='editor',
            field=models.ForeignKey(to='staff.StaffPage', related_name='public_donorpage_editor', on_delete=django.db.models.deletion.SET_NULL, null=True),
        ),
        migrations.AddField(
            model_name='donorpage',
            name='image',
            field=models.ForeignKey(to='wagtailimages.Image', on_delete=django.db.models.deletion.SET_NULL, related_name='+', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='donorpage',
            name='page_maintainer',
            field=models.ForeignKey(to='staff.StaffPage', related_name='public_donorpage_maintainer', on_delete=django.db.models.deletion.SET_NULL, null=True),
        ),
        migrations.AddField(
            model_name='donorpage',
            name='unit',
            field=models.ForeignKey(to='units.UnitPage', on_delete=django.db.models.deletion.SET_NULL, related_name='public_donorpage_related', blank=True, null=True),
        ),
    ]
