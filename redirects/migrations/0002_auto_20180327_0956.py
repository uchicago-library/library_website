# Generated by Django 2.0.3 on 2018-03-27 14:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('redirects', '0001_squashed_0021_auto_20161104_1314'),
    ]

    operations = [
        migrations.AlterField(
            model_name='redirectpage',
            name='unit',
            field=models.ForeignKey(limit_choices_to={'display_in_dropdown': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='redirects_redirectpage_related', to='units.UnitPage'),
        ),
    ]
