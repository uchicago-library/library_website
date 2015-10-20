# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0025_donorpage'),
        ('lib_collections', '0014_auto_20151019_1756'),
    ]

    operations = [
        migrations.CreateModel(
            name='DonorPageListPlacement',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('sort_order', models.IntegerField(blank=True, null=True, editable=False)),
                ('donor', models.ForeignKey(blank=True, related_name='donor_page', on_delete=django.db.models.deletion.SET_NULL, null=True, to='public.DonorPage')),
                ('parent', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.SET_NULL, related_name='donor_page_list_placement', null=True, to='lib_collections.CollectionPage')),
            ],
            options={
                'abstract': False,
                'ordering': ['sort_order'],
            },
        ),
    ]
