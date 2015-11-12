# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0002_auto_20151111_2026'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newspage',
            name='excerpt',
            field=wagtail.wagtailcore.fields.RichTextField(),
        ),
    ]
