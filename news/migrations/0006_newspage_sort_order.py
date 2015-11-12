# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0005_newspage_publish_on'),
    ]

    operations = [
        migrations.AddField(
            model_name='newspage',
            name='sort_order',
            field=models.IntegerField(default=0, blank=True),
        ),
    ]
