# Generated by Django 2.0.12 on 2020-02-19 21:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0021_auto_20200219_1534'),
    ]

    operations = [
        migrations.AddField(
            model_name='collectionpagefacet',
            name='includes_ocr',
            field=models.BooleanField(default=False, help_text='Does this include OCR?'),
        ),
        migrations.AddField(
            model_name='collectionpagesearch',
            name='includes_ocr',
            field=models.BooleanField(default=False, help_text='Does this include OCR?'),
        ),
        migrations.AlterField(
            model_name='collectionpagesearch',
            name='default',
            field=models.BooleanField(default=False, help_text='Is this the default search?'),
        ),
    ]