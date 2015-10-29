# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0016_vcard_email'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='vcard',
            options={'ordering': ['sort_order']},
        ),
        migrations.RemoveField(
            model_name='staffpagepagevcards',
            name='sort_order',
        ),
        migrations.AddField(
            model_name='vcard',
            name='sort_order',
            field=models.IntegerField(null=True, blank=True, editable=False),
        ),
    ]
