# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0006_add_verbose_names'),
        ('wagtailcore', '0001_squashed_0016_change_page_url_path_to_text_field'),
    ]

    operations = [
        migrations.CreateModel(
            name='StaffIndexPage',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('intro', models.TextField()),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='StaffPage',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('last_name', models.CharField(max_length=255)),
                ('first_name', models.CharField(max_length=255)),
                ('job_title', models.CharField(max_length=255)),
                ('room', models.CharField(max_length=255)),
                ('email', models.CharField(max_length=255, validators=[django.core.validators.EmailValidator()])),
                ('phone', models.CharField(blank=True, max_length=8, validators=[django.core.validators.RegexValidator(b'^[0-9]{3}-[0-9]{4}$', b'Enter phone numbers in the following form: 702-1234.')])),
                ('portrait_image', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='wagtailimages.Image', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]
