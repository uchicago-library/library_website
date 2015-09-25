# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0017_basepage_description'),
        ('public', '0008_auto_20150807_2148'),
    ]

    operations = [
        migrations.CreateModel(
            name='LocationPage',
            fields=[
                ('basepage_ptr', models.OneToOneField(serialize=False, to='base.BasePage', auto_created=True, parent_link=True, primary_key=True)),
                ('name', models.CharField(max_length=45)),
                ('is_building', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
            bases=('base.basepage',),
        ),
    ]
