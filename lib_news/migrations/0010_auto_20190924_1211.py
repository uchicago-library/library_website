# Generated by Django 2.0.12 on 2019-09-24 17:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lib_news', '0009_auto_20190917_1658'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='libnewsindexpage',
            name='news_feed_url',
        ),
        migrations.RemoveField(
            model_name='libnewspage',
            name='news_feed_url',
        ),
    ]