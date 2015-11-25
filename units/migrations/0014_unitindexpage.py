# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0020_add_index_on_page_first_published_at'),
        ('units', '0013_auto_20151124_0008'),
    ]

    operations = [
        migrations.CreateModel(
            name='UnitIndexPage',
            fields=[
                ('page_ptr', models.OneToOneField(primary_key=True, parent_link=True, serialize=False, auto_created=True, to='wagtailcore.Page')),
                ('intro', wagtail.wagtailcore.fields.RichTextField()),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]
