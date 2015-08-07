# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0015_auto_20150807_2056'),
        ('public', '0002_auto_20150807_2102'),
    ]

    operations = [
        migrations.CreateModel(
            name='StandardPage',
            fields=[
                ('basepage_ptr', models.OneToOneField(primary_key=True, auto_created=True, serialize=False, parent_link=True, to='base.BasePage')),
                ('foo', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
            bases=('base.basepage',),
        ),
    ]
