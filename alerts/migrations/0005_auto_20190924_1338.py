# Generated by Django 2.0.12 on 2019-09-24 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alerts', '0004_auto_20190924_1211'),
    ]

    operations = [
        migrations.AddField(
            model_name='alertindexpage',
            name='news_feed_source',
            field=models.CharField(blank=True, choices=[('', '--------'), ('library_kiosk', 'Library'), ('law_kiosk', 'Law'), ('crerar_kiosk', 'Crerar'), ('scrc_kiosk', 'SCRC')], default='', max_length=50),
        ),
        migrations.AddField(
            model_name='alertpage',
            name='news_feed_source',
            field=models.CharField(blank=True, choices=[('', '--------'), ('library_kiosk', 'Library'), ('law_kiosk', 'Law'), ('crerar_kiosk', 'Crerar'), ('scrc_kiosk', 'SCRC')], default='', max_length=50),
        ),
    ]
