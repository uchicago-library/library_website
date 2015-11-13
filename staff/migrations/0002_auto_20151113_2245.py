# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('subjects', '0001_initial'),
        ('units', '0001_initial'),
        ('wagtailimages', '0008_image_created_at_index'),
        ('wagtaildocs', '0003_add_verbose_names'),
        ('staff', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='vcard',
            name='unit',
            field=models.ForeignKey(to='units.UnitPage', on_delete=django.db.models.deletion.SET_NULL, related_name='staff_vcard_related', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='staffpagesubjectplacement',
            name='page',
            field=modelcluster.fields.ParentalKey(related_name='staff_subject_placements', to='staff.StaffPage'),
        ),
        migrations.AddField(
            model_name='staffpagesubjectplacement',
            name='subject',
            field=models.ForeignKey(related_name='+', to='subjects.Subject'),
        ),
        migrations.AddField(
            model_name='staffpage',
            name='cv',
            field=models.ForeignKey(to='wagtaildocs.Document', on_delete=django.db.models.deletion.SET_NULL, related_name='+', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='staffpage',
            name='profile_picture',
            field=models.ForeignKey(to='wagtailimages.Image', on_delete=django.db.models.deletion.SET_NULL, related_name='+', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='staffpage',
            name='supervisor',
            field=models.ForeignKey(to='staff.StaffPage', on_delete=django.db.models.deletion.SET_NULL, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='staffpagepagevcards',
            name='page',
            field=modelcluster.fields.ParentalKey(related_name='vcards', to='staff.StaffPage'),
        ),
    ]
