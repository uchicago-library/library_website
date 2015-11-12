# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0008_image_created_at_index'),
        ('subjects', '0001_initial'),
        ('wagtaildocs', '0003_add_verbose_names'),
        ('units', '0001_initial'),
        ('staff', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='vcard',
            name='unit',
            field=models.ForeignKey(related_name='staff_vcard_related', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='units.UnitPage', null=True),
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
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='wagtaildocs.Document', null=True),
        ),
        migrations.AddField(
            model_name='staffpage',
            name='editor',
            field=models.ForeignKey(related_name='staff_staffpage_editor', on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True),
        ),
        migrations.AddField(
            model_name='staffpage',
            name='page_maintainer',
            field=models.ForeignKey(related_name='staff_staffpage_maintainer', on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True),
        ),
        migrations.AddField(
            model_name='staffpage',
            name='profile_picture',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='wagtailimages.Image', null=True),
        ),
        migrations.AddField(
            model_name='staffpage',
            name='supervisor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='staff.StaffPage', null=True),
        ),
        migrations.AddField(
            model_name='staffpagepagevcards',
            name='page',
            field=modelcluster.fields.ParentalKey(related_name='vcards', to='staff.StaffPage'),
        ),
    ]
