# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0020_add_index_on_page_first_published_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='StaffIndexPage',
            fields=[
                ('page_ptr', models.OneToOneField(serialize=False, primary_key=True, parent_link=True, to='wagtailcore.Page', auto_created=True)),
                ('intro', wagtail.wagtailcore.fields.RichTextField()),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='StaffPage',
            fields=[
                ('page_ptr', models.OneToOneField(serialize=False, primary_key=True, parent_link=True, to='wagtailcore.Page', auto_created=True)),
                ('cnetid', models.CharField(max_length=255)),
                ('display_name', models.CharField(null=True, max_length=255, blank=True)),
                ('official_name', models.CharField(null=True, max_length=255, blank=True)),
                ('first_name', models.CharField(null=True, max_length=255, blank=True)),
                ('middle_name', models.CharField(null=True, max_length=255, blank=True)),
                ('last_name', models.CharField(null=True, max_length=255, blank=True)),
                ('libguide_url', models.URLField(null=True, max_length=255, blank=True)),
                ('bio', wagtail.wagtailcore.fields.RichTextField(blank=True, null=True)),
                ('is_public_persona', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='StaffPageSubjectPlacement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('sort_order', models.IntegerField(editable=False, blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Subject Placement',
                'verbose_name_plural': 'Subject Placements',
            },
        ),
        migrations.CreateModel(
            name='VCard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('email', models.EmailField(max_length=254, blank=True)),
                ('phone_label', models.CharField(max_length=25, blank=True)),
                ('phone_number', models.CharField(validators=[django.core.validators.RegexValidator(regex='^[0-9]{3}-[0-9]{3}-[0-9]{4}$', message='Please enter the phone number using the format 773-123-4567')], max_length=12, blank=True)),
                ('title', models.CharField(max_length=255)),
                ('faculty_exchange', models.CharField(max_length=255, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='StaffPagePageVCards',
            fields=[
                ('vcard_ptr', models.OneToOneField(serialize=False, primary_key=True, parent_link=True, to='staff.VCard', auto_created=True)),
                ('sort_order', models.IntegerField(editable=False, blank=True, null=True)),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
            bases=('staff.vcard', models.Model),
        ),
    ]
