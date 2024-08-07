# Generated by Django 3.2.15 on 2022-12-09 00:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0051_auto_20220920_1154'),
    ]

    operations = [
        migrations.AddField(
            model_name='exhibitpage',
            name='font_kerning',
            field=models.FloatField(blank=True, help_text='Enter a positive number to increase spacing between letters, or a negative number to reduce spacing. Decimal values are okay. e.g. 2.5 or -1.25', null=True),
        ),
        migrations.AddField(
            model_name='exhibitpage',
            name='font_scaler',
            field=models.FloatField(blank=True, help_text='Enter a value between 0 and 1 for a smaller font. Enter a value greater than 1 for a larger font. e.g. 0.5, 1.5, or 2', null=True),
        ),
    ]
