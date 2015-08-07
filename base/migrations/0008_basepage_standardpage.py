# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0001_squashed_0016_change_page_url_path_to_text_field'),
        ('base', '0007_auto_20150807_1848'),
    ]

    operations = [
        migrations.CreateModel(
            name='BasePage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, primary_key=True, to='wagtailcore.Page', serialize=False, parent_link=True)),
                ('description', models.TextField()),
                ('last_reviewed', models.DateField(verbose_name='Did you review this page?', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='StandardPage',
            fields=[
                ('basepage_ptr', models.OneToOneField(auto_created=True, primary_key=True, to='base.BasePage', serialize=False, parent_link=True)),
                ('foo', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
            bases=('base.basepage',),
        ),
    ]
