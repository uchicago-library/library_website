# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('subjects', '0002_auto_20151022_1913'),
        ('lib_collections', '0061_auto_20151029_1448'),
    ]

    operations = [
        migrations.CreateModel(
            name='CollectionPageSubjectPlacement',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('sort_order', models.IntegerField(editable=False, blank=True, null=True)),
                ('format', models.ForeignKey(to='subjects.Subject', related_name='+')),
                ('page', modelcluster.fields.ParentalKey(to='lib_collections.CollectionPage', related_name='collection_subject_placements')),
            ],
            options={
                'verbose_name': 'Subject Placement',
                'verbose_name_plural': 'Subbject Placements',
            },
        ),
    ]
