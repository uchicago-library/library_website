# Generated by Django 2.0.8 on 2018-12-21 17:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('searchable_content', '0006_auto_20181221_0934'),
    ]

    operations = [
        migrations.CreateModel(
            name='LibGuidesAssetsSearchableContent',
            fields=[
                ('searchablecontent_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='searchable_content.SearchableContent')),
            ],
            bases=('searchable_content.searchablecontent',),
        ),
    ]
