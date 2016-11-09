# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0020_add_index_on_page_first_published_at'),
        ('directory_unit', '0002_auto_20151208_1739'),
        ('staff', '0000_manual_pre_initial'),
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
        migrations.AddField(
            model_name='staff',
            name='cnetid',
            field=models.CharField(blank=True, max_length=255),
        ),  
        migrations.AddField(
            model_name='staff',
            name='display_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),  
        migrations.AddField(
            model_name='staff',
            name='official_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),  
        migrations.AddField(
            model_name='staff',
            name='first_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),  
        migrations.AddField(
            model_name='staff',
            name='middle_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),  
        migrations.AddField(
            model_name='staff',
            name='last_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),  
        migrations.AddField(
            model_name='staff',
            name='libguide_url',
            field=models.URLField(blank=True, max_length=255, null=True),
        ), 
        migrations.AddField(
            model_name='staff',
            name='bio',
            field=wagtail.wagtailcore.fields.RichTextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='staff',
            name='is_public_persona',
            field=models.BooleanField(default=False),
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
