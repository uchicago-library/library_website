# Generated by Django 2.0.12 on 2020-02-24 21:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0037_remove_collectionpage_object_identifier'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='collectionpage',
            name='display_location',
        ),
        migrations.AlterField(
            model_name='collectionpageexternalservice',
            name='service',
            field=models.IntegerField(choices=[(1, 'LUNA'), (2, 'BTAA')], default=1, help_text='Choose an external service'),
        ),
    ]
