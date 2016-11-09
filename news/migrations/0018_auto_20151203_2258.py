# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0000_manual_pre_initial'),
        ('news', '0017_auto_20151203_1806'),
    ]

    operations = [
        migrations.RenameField(
            model_name='newspage',
            old_name='thumbnail_image',
            new_name='image',
        ),
        migrations.RenameField(
            model_name='newspage',
            old_name='publish_on',
            new_name='story_date',
        ),
        migrations.AddField(
            model_name='newspage',
            name='author',
            field=models.ForeignKey(blank=True, null=True, related_name='news_stories', on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage'),
        ),
    ]
