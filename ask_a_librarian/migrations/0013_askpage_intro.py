# Generated by Django 2.0.12 on 2020-03-08 01:24

from django.db import migrations
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ask_a_librarian', '0012_auto_20200327_1843'),
    ]

    operations = [
        migrations.AddField(
            model_name='askpage',
            name='intro',
            field=wagtail.fields.RichTextField(blank=True, null=True),
        ),
    ]
