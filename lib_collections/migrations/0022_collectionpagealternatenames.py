# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0021_auto_20151019_1936'),
    ]

    operations = [
        migrations.CreateModel(
            name='CollectionPageAlternateNames',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(editable=False, null=True, blank=True)),
                ('alternate_name', models.CharField(max_length=255)),
                ('page', modelcluster.fields.ParentalKey(related_name='alternate_name', to='lib_collections.CollectionPage')),
            ],
            options={
                'abstract': False,
                'ordering': ['sort_order'],
            },
        ),
    ]
