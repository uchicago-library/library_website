# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0008_image_created_at_index'),
        ('wagtailcore', '0019_verbose_names_cleanup'),
        ('wagtaildocs', '0003_add_verbose_names'),
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
                ('cnetid', models.CharField(max_length=255, null=True, blank=True)),
                ('official_name', models.CharField(max_length=255, null=True, blank=True)),
                ('display_name', models.CharField(max_length=255, null=True, blank=True)),
                ('alphabetize_name_as', models.CharField(max_length=255, null=True, blank=True)),
                ('email', models.CharField(blank=True, max_length=255, null=True, validators=[django.core.validators.EmailValidator()])),
                ('libguide_url', models.CharField(max_length=255, null=True, blank=True)),
                ('bio', models.TextField(null=True, blank=True)),
                ('is_public_persona', models.BooleanField(default=False)),
                ('cv', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='wagtaildocs.Document', null=True)),
                ('profile_picture', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='wagtailimages.Image', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='StaffTitle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('department', models.CharField(max_length=255)),
                ('sub_department', models.CharField(max_length=255)),
                ('phone', models.CharField(max_length=255)),
                ('faculty_exchange', models.CharField(max_length=255)),
                ('staff', models.ForeignKey(to='staff.StaffPage')),
            ],
        ),
    ]
