# Generated by Django 2.0.12 on 2020-02-19 21:17

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0016_collectionpageclusterbrowse'),
    ]

    operations = [
        migrations.CreateModel(
            name='CollectionPageFacet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('col_facet', models.CharField(blank=True, max_length=255)),
                ('include', models.BooleanField(default=False, help_text='Include in sidebar?')),
                ('page', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='col_facet', to='lib_collections.CollectionPage')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
    ]