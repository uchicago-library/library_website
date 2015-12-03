# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0016_auto_20151202_1651'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newsindexpage',
            name='editor',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='news_newsindexpage_editor', null=True),
        ),
        migrations.AlterField(
            model_name='newsindexpage',
            name='page_maintainer',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='news_newsindexpage_maintainer', null=True),
        ),
        migrations.AlterField(
            model_name='newspage',
            name='editor',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='news_newspage_editor', null=True),
        ),
        migrations.AlterField(
            model_name='newspage',
            name='page_maintainer',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='news_newspage_maintainer', null=True),
        ),
    ]
