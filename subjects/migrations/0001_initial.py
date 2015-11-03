# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import wagtail.wagtailsearch.index


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('parent_location', models.ForeignKey(blank=True, null=True, to='subjects.Subject', on_delete=django.db.models.deletion.SET_NULL)),
            ],
            bases=(models.Model, wagtail.wagtailsearch.index.Indexed),
        ),
    ]
