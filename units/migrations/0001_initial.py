# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0019_verbose_names_cleanup'),
        ('public', '0025_donorpage'),
    ]

    operations = [
        migrations.CreateModel(
            name='UnitPage',
            fields=[
                ('page_ptr', models.OneToOneField(serialize=False, auto_created=True, primary_key=True, to='wagtailcore.Page', parent_link=True)),
                ('description', models.TextField(blank=True)),
                ('last_reviewed', models.DateTimeField(verbose_name='Last Reviewed', blank=True, null=True)),
                ('display_in_directory', models.BooleanField(default=False)),
                ('location', models.ForeignKey(blank=True, related_name='units_unitpage_related', on_delete=django.db.models.deletion.SET_NULL, null=True, to='public.LocationPage')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]
