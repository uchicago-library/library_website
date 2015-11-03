# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0025_donorpage'),
        ('lib_collections', '0020_remove_collectionpage_donor'),
    ]

    operations = [
        migrations.CreateModel(
            name='DonorPagePlacement',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('sort_order', models.IntegerField(blank=True, null=True, editable=False)),
                ('donor', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, null=True, related_name='donor_page', to='public.DonorPage', blank=True)),
                ('parent', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.SET_NULL, related_name='donor_page_list_placement', null=True, to='lib_collections.CollectionPage')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='donorpagelistplacement',
            name='donor',
        ),
        migrations.RemoveField(
            model_name='donorpagelistplacement',
            name='parent',
        ),
        migrations.DeleteModel(
            name='DonorPageListPlacement',
        ),
    ]
