# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0062_collectionpagesubjectplacement'),
    ]

    operations = [
        migrations.RenameField(
            model_name='collectionpagesubjectplacement',
            old_name='format',
            new_name='subject',
        ),
    ]
