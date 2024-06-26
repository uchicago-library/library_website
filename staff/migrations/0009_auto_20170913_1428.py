# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-09-13 19:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0008_auto_20170719_1020'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staffpage',
            name='employee_type',
            field=models.IntegerField(choices=[(1, 'Clerical'), (2, 'Exempt'), (3, 'IT'), (4, 'Librarian'), (5, 'Non-exempt')], default=1, help_text='Clerical, exempt, IT or Librarian.'),
        ),
    ]
