# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0003_auto_20151112_1550'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newspage',
            name='excerpt',
            field=wagtail.wagtailcore.fields.RichTextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='newspage',
            name='sticky_until',
            field=models.DateField(null=True, blank=True),
        ),
    ]
