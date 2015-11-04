# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0010_auto_20151104_2017'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupPageReports',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('sort_order', models.IntegerField(blank=True, null=True, editable=False)),
                ('date', models.DateField()),
                ('summary', models.TextField()),
                ('link', models.URLField(default='', max_length=254)),
                ('page', modelcluster.fields.ParentalKey(to='group.GroupPage', related_name='group_reports')),
            ],
            options={
                'abstract': False,
                'ordering': ['sort_order'],
            },
        ),
    ]
