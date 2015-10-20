# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0019_verbose_names_cleanup'),
        ('public', '0024_auto_20151016_1541'),
    ]

    operations = [
        migrations.CreateModel(
            name='DonorPage',
            fields=[
                ('page_ptr', models.OneToOneField(to='wagtailcore.Page', auto_created=True, primary_key=True, serialize=False, parent_link=True)),
                ('description', models.TextField(blank=True)),
                ('last_reviewed', models.DateTimeField(null=True, verbose_name='Last Reviewed', blank=True)),
                ('foobar', models.CharField(max_length=255)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='public.LocationPage', blank=True, related_name='public_donorpage_related', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]
