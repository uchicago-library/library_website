# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0019_auto_20151124_0008'),
    ]

    operations = [
        migrations.AddField(
            model_name='donorpage',
            name='show_sidebar',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='donorpage',
            name='subsection_start',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='floorplanpage',
            name='show_sidebar',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='floorplanpage',
            name='subsection_start',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='locationpage',
            name='show_sidebar',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='locationpage',
            name='subsection_start',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='standardpage',
            name='show_sidebar',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='standardpage',
            name='subsection_start',
            field=models.BooleanField(default=False),
        ),
    ]
