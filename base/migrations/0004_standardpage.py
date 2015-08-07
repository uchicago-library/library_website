# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_auto_20150807_1741'),
    ]

    operations = [
        migrations.CreateModel(
            name='StandardPage',
            fields=[
                ('basepage_ptr', models.OneToOneField(serialize=False, auto_created=True, to='base.BasePage', parent_link=True, primary_key=True)),
                ('foo', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
            bases=('base.basepage',),
        ),
    ]
