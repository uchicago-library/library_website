# Generated by Django 2.0.8 on 2018-11-16 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0007_auto_20180327_0956'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grouppage',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]