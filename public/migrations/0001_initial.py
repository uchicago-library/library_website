# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0014_auto_20150807_2049'),
    ]

    operations = [
        migrations.CreateModel(
            name='StandardPage',
            fields=[
                ('basepage_ptr', models.OneToOneField(auto_created=True, to='base.BasePage', serialize=False, parent_link=True, primary_key=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('base.basepage',),
        ),
    ]
