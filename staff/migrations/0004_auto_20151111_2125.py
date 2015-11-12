# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0003_auto_20151111_2122'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staffpage',
            name='bio',
            field=wagtail.wagtailcore.fields.RichTextField(blank=True),
        ),
    ]
