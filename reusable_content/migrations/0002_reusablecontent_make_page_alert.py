# Generated by Django 2.0.12 on 2020-03-07 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reusable_content', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='reusablecontent',
            name='make_page_alert',
            field=models.BooleanField(default=False, help_text='Display as in-page alert'),
        ),
    ]
