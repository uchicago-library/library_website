# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0059_auto_20151027_2224'),
    ]

    operations = [
        migrations.CreateModel(
            name='CollectingAreaPageLibGuides',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('sort_order', models.IntegerField(null=True, editable=False, blank=True)),
                ('guide_link_text', models.CharField(default='', max_length=255)),
                ('guide_link_url', models.URLField(default='', verbose_name='Libguide URL')),
                ('page', modelcluster.fields.ParentalKey(to='lib_collections.CollectingAreaPage', related_name='lib_guides')),
            ],
            options={
                'abstract': False,
                'ordering': ['sort_order'],
            },
        ),
    ]
