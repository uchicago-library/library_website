# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0026_auto_20151029_1844'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='staffpagepagevcards',
            name='page',
        ),
        migrations.RemoveField(
            model_name='staffpagepagevcards',
            name='vcard_ptr',
        ),
        migrations.RemoveField(
            model_name='vcard',
            name='unit',
        ),
        migrations.DeleteModel(
            name='StaffPagePageVCards',
        ),
        migrations.DeleteModel(
            name='VCard',
        ),
    ]
