# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0007_auto_20151016_2044'),
    ]

    operations = [
        migrations.RenameField(
            model_name='collectionpageformatplacement',
            old_name='advert',
            new_name='format',
        ),
    ]
