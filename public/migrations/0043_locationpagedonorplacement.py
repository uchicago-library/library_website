# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0042_donorpage_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='LocationPageDonorPlacement',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('sort_order', models.IntegerField(null=True, editable=False, blank=True)),
                ('donor', models.ForeignKey(blank=True, related_name='location_donor_page', on_delete=django.db.models.deletion.SET_NULL, null=True, to='public.DonorPage')),
                ('parent', modelcluster.fields.ParentalKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='public.LocationPage', related_name='location_donor_page_placements')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
    ]
