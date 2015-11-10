# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0008_image_created_at_index'),
        ('public', '0002_auto_20151110_1511'),
        ('staff', '0001_initial'),
        ('units', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='standardpage',
            name='unit',
            field=models.ForeignKey(related_name='public_standardpage_related', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='units.UnitPage', null=True),
        ),
        migrations.AddField(
            model_name='locationpagedonorplacement',
            name='donor',
            field=models.ForeignKey(related_name='location_donor_page', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='public.DonorPage', null=True),
        ),
        migrations.AddField(
            model_name='locationpagedonorplacement',
            name='parent',
            field=modelcluster.fields.ParentalKey(related_name='location_donor_page_placements', on_delete=django.db.models.deletion.SET_NULL, to='public.LocationPage', null=True),
        ),
        migrations.AddField(
            model_name='locationpage',
            name='content_specialist',
            field=models.ForeignKey(related_name='public_locationpage_content_specialist', on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True),
        ),
        migrations.AddField(
            model_name='locationpage',
            name='editor',
            field=models.ForeignKey(related_name='public_locationpage_editor', on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True),
        ),
        migrations.AddField(
            model_name='locationpage',
            name='location_photo',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='wagtailimages.Image', null=True),
        ),
        migrations.AddField(
            model_name='locationpage',
            name='page_maintainer',
            field=models.ForeignKey(related_name='public_locationpage_maintainer', on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True),
        ),
        migrations.AddField(
            model_name='locationpage',
            name='parent_building',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='public.LocationPage', null=True),
        ),
        migrations.AddField(
            model_name='locationpage',
            name='unit',
            field=models.ForeignKey(related_name='public_locationpage_related', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='units.UnitPage', null=True),
        ),
        migrations.AddField(
            model_name='donorpage',
            name='content_specialist',
            field=models.ForeignKey(related_name='public_donorpage_content_specialist', on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True),
        ),
        migrations.AddField(
            model_name='donorpage',
            name='editor',
            field=models.ForeignKey(related_name='public_donorpage_editor', on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True),
        ),
        migrations.AddField(
            model_name='donorpage',
            name='image',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='wagtailimages.Image', null=True),
        ),
        migrations.AddField(
            model_name='donorpage',
            name='page_maintainer',
            field=models.ForeignKey(related_name='public_donorpage_maintainer', on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True),
        ),
        migrations.AddField(
            model_name='donorpage',
            name='unit',
            field=models.ForeignKey(related_name='public_donorpage_related', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='units.UnitPage', null=True),
        ),
    ]
