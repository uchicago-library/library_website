# Generated by Django 2.0.8 on 2018-12-03 22:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('searchable_content', '0004_searchablecontent_identifier'),
    ]

    operations = [
        migrations.AlterField(
            model_name='searchablecontent',
            name='datestamp',
            field=models.DateTimeField(verbose_name='datestamp'),
        ),
    ]
