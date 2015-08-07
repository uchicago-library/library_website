# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0001_squashed_0016_change_page_url_path_to_text_field'),
    ]

    operations = [
        migrations.CreateModel(
            name='BasePage',
            fields=[
                ('page_ptr', models.OneToOneField(to='wagtailcore.Page', primary_key=True, serialize=False, auto_created=True, parent_link=True)),
                ('description', models.TextField()),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]
