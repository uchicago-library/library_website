# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0001_initial'),
        ('news', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='newsindexpage',
            name='editor',
            field=models.ForeignKey(related_name='news_newsindexpage_editor', on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True),
        ),
        migrations.AddField(
            model_name='newsindexpage',
            name='last_reviewed',
            field=models.DateTimeField(null=True, verbose_name=b'Last Reviewed', blank=True),
        ),
        migrations.AddField(
            model_name='newsindexpage',
            name='page_maintainer',
            field=models.ForeignKey(related_name='news_newsindexpage_maintainer', on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True),
        ),
        migrations.AddField(
            model_name='newspage',
            name='editor',
            field=models.ForeignKey(related_name='news_newspage_editor', on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True),
        ),
        migrations.AddField(
            model_name='newspage',
            name='last_reviewed',
            field=models.DateTimeField(null=True, verbose_name=b'Last Reviewed', blank=True),
        ),
        migrations.AddField(
            model_name='newspage',
            name='page_maintainer',
            field=models.ForeignKey(related_name='news_newspage_maintainer', on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True),
        ),
    ]
