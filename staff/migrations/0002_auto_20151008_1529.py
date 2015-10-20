# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtaildocs', '0003_add_verbose_names'),
        ('staff', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StaffTitle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('department', models.CharField(max_length=255)),
                ('sub_department', models.CharField(max_length=255)),
                ('phone', models.CharField(max_length=255)),
                ('faculty_exchange', models.CharField(max_length=255)),
            ],
        ),
        migrations.RenameField(
            model_name='staffpage',
            old_name='portrait_image',
            new_name='profile_picture',
        ),
        migrations.RemoveField(
            model_name='staffpage',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='staffpage',
            name='job_title',
        ),
        migrations.RemoveField(
            model_name='staffpage',
            name='last_name',
        ),
        migrations.RemoveField(
            model_name='staffpage',
            name='phone',
        ),
        migrations.RemoveField(
            model_name='staffpage',
            name='room',
        ),
        migrations.AddField(
            model_name='staffpage',
            name='alphabetize_name_as',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='staffpage',
            name='bio',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='staffpage',
            name='cnetid',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='staffpage',
            name='cv',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='wagtaildocs.Document', null=True),
        ),
        migrations.AddField(
            model_name='staffpage',
            name='display_name',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='staffpage',
            name='is_public_persona',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='staffpage',
            name='libguide_url',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='staffpage',
            name='official_name',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stafftitle',
            name='staff',
            field=models.ForeignKey(to='staff.StaffPage'),
        ),
    ]
