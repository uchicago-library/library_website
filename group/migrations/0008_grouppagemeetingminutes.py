# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0007_auto_20151031_0332'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupPageMeetingMinutes',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(editable=False, blank=True, null=True)),
                ('date', models.DateField()),
                ('summary', models.TextField()),
                ('link', models.URLField(default='', max_length=254)),
                ('page', modelcluster.fields.ParentalKey(to='group.GroupPage', related_name='meeting_minutes')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
    ]
