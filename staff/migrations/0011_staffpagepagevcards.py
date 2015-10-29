# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0010_auto_20151029_1749'),
    ]

    operations = [
        migrations.CreateModel(
            name='StaffPagePageVCards',
            fields=[
                ('vcard_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, to='staff.VCard', serialize=False)),
                ('sort_order', models.IntegerField(null=True, blank=True, editable=False)),
                ('page', modelcluster.fields.ParentalKey(to='staff.StaffPage', related_name='vcards')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
            bases=('staff.vcard', models.Model),
        ),
    ]
