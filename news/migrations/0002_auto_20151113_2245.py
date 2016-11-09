# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0001_initial'),
        ('staff', '0000_manual_pre_initial'),
        ('wagtailimages', '0008_image_created_at_index'),
    ]

    operations = [
        migrations.AddField(
            model_name='newspage',
            name='editor',
            field=models.ForeignKey(to='staff.StaffPage', related_name='news_newspage_editor', on_delete=django.db.models.deletion.SET_NULL, null=True),
        ),
        migrations.AddField(
            model_name='newspage',
            name='page_maintainer',
            field=models.ForeignKey(to='staff.StaffPage', related_name='news_newspage_maintainer', on_delete=django.db.models.deletion.SET_NULL, null=True),
        ),
        migrations.AddField(
            model_name='newspage',
            name='thumbnail_image',
            field=models.ForeignKey(to='wagtailimages.Image', on_delete=django.db.models.deletion.SET_NULL, related_name='+', blank=True, null=True),
        ),
    ]
