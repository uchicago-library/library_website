# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-16 17:27
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0069_auto_20160614_1901'),
    ]

    operations = [
        migrations.AddField(
            model_name='donorpage',
            name='quicklinks',
            field=wagtail.fields.RichTextField(blank=True),
        ),
        migrations.AddField(
            model_name='donorpage',
            name='quicklinks_title',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='donorpage',
            name='view_more_link',
            field=models.URLField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='donorpage',
            name='view_more_link_label',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='floorplanpage',
            name='quicklinks',
            field=wagtail.fields.RichTextField(blank=True),
        ),
        migrations.AddField(
            model_name='floorplanpage',
            name='quicklinks_title',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='floorplanpage',
            name='view_more_link',
            field=models.URLField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='floorplanpage',
            name='view_more_link_label',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='locationpage',
            name='quicklinks',
            field=wagtail.fields.RichTextField(blank=True),
        ),
        migrations.AddField(
            model_name='locationpage',
            name='quicklinks_title',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='locationpage',
            name='view_more_link',
            field=models.URLField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='locationpage',
            name='view_more_link_label',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='publicrawhtmlpage',
            name='quicklinks',
            field=wagtail.fields.RichTextField(blank=True),
        ),
        migrations.AddField(
            model_name='publicrawhtmlpage',
            name='quicklinks_title',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='publicrawhtmlpage',
            name='view_more_link',
            field=models.URLField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='publicrawhtmlpage',
            name='view_more_link_label',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='staffpublicpage',
            name='quicklinks',
            field=wagtail.fields.RichTextField(blank=True),
        ),
        migrations.AddField(
            model_name='staffpublicpage',
            name='quicklinks_title',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='staffpublicpage',
            name='view_more_link',
            field=models.URLField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='staffpublicpage',
            name='view_more_link_label',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
