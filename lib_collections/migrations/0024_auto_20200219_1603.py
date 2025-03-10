# Generated by Django 2.0.12 on 2020-02-19 22:03

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0023_auto_20200219_1558'),
    ]

    operations = [
        migrations.CreateModel(
            name='CollectionPageMetadata',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('documentation', models.CharField(blank=True, max_length=255)),
                ('location', models.URLField(blank=True, max_length=255)),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='collectionpage',
            name='metadata',
        ),
        migrations.AddField(
            model_name='collectionpagemetadata',
            name='page',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='col_metadata', to='lib_collections.CollectionPage'),
        ),
    ]
