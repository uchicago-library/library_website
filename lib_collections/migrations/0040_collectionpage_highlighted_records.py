# Generated by Django 2.0.12 on 2020-02-24 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0039_auto_20200224_1504'),
    ]

    operations = [
        migrations.AddField(
            model_name='collectionpage',
            name='highlighted_records',
            field=models.URLField(blank=True, help_text='URL for browse index in IIIF to display\n            results on collection parent page'),
        ),
    ]
