# Generated by Django 2.0.12 on 2020-02-24 20:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0031_auto_20200224_1422'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='collectionpage',
            name='search_bar',
        ),
    ]