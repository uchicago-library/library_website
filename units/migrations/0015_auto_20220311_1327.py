# Generated by Django 3.1.12 on 2022-03-11 19:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0014_auto_20210706_1515'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unitpage',
            name='building',
            field=models.IntegerField(choices=[(1, 'The John Crerar Library'), (2, "The D'Angelo Law Library"), (3, 'Eckhart Library'), (4, 'The Joe and Rika Mansueto Library'), (5, 'The Joseph Regenstein Library'), (6, 'The Hanna Holborn Gray Special Collections Research Center'), (7, 'The Social Work Library'), (8, 'Ryerson Physical Laboratory')], default=5, help_text='The physical building where this unit is located.'),
        ),
    ]