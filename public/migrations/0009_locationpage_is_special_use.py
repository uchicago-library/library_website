# Generated by Django 2.0.3 on 2018-05-25 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0008_auto_20180327_0956'),
    ]

    operations = [
        migrations.AddField(
            model_name='locationpage',
            name='is_special_use',
            field=models.BooleanField(default=False),
        ),
    ]
