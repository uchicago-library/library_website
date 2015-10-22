# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import modelcluster.fields
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0035_auto_20151022_1855'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubjectSpecialistPlacement',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('sort_order', models.IntegerField(editable=False, blank=True, null=True)),
            ],
            options={
                'abstract': False,
                'ordering': ['sort_order'],
            },
        ),
        migrations.RemoveField(
            model_name='collectingareapage',
            name='subject_specialist',
        ),
        migrations.AddField(
            model_name='subjectspecialistplacement',
            name='parent',
            field=modelcluster.fields.ParentalKey(blank=True, related_name='subject_specialist_placement', on_delete=django.db.models.deletion.SET_NULL, to='lib_collections.CollectingAreaPage', null=True),
        ),
        migrations.AddField(
            model_name='subjectspecialistplacement',
            name='subject_specialist',
            field=models.ForeignKey(blank=True, related_name='subject_specialist', on_delete=django.db.models.deletion.SET_NULL, to='lib_collections.CollectingAreaPage', null=True),
        ),
    ]
