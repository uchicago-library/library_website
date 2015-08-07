# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailredirects', '0002_add_verbose_names'),
        ('wagtailcore', '0001_squashed_0016_change_page_url_path_to_text_field'),
        ('wagtailsearch', '0002_add_verbose_names'),
        ('wagtailforms', '0002_add_verbose_names'),
        ('base', '0002_auto_20150807_1733'),
    ]

    operations = [
        migrations.CreateModel(
            name='BasePage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, to='wagtailcore.Page', parent_link=True, serialize=False, primary_key=True)),
                ('description', models.TextField()),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.RemoveField(
            model_name='standardpage',
            name='page_ptr',
        ),
        migrations.DeleteModel(
            name='StandardPage',
        ),
    ]
