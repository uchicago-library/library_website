# Generated by Django 2.0.12 on 2019-07-10 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conferences', '0006_auto_20180327_0956'),
    ]

    operations = [
        migrations.AddField(
            model_name='conferenceindexpage',
            name='display_current_web_exhibits',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='conferencepage',
            name='display_current_web_exhibits',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='conferencesubpage',
            name='display_current_web_exhibits',
            field=models.BooleanField(default=False),
        ),
    ]
