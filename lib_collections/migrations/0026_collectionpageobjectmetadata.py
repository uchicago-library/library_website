# Generated by Django 2.0.12 on 2020-02-20 19:39

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0025_collectionpageresult'),
    ]

    operations = [
        migrations.CreateModel(
            name='CollectionPageObjectMetadata',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('edm_field_label', models.CharField(blank=True, max_length=255)),
                ('hotlinked', models.BooleanField(default=False, help_text='Is this EDM field hotlinked?')),
                ('multiple_values', models.BooleanField(default=False, help_text='Are there multiple values within the field?')),
                ('link_target', models.IntegerField(choices=[(1, 'go to a results page for the selected item'), (2, 'link to a related item in the collection')], default=1, help_text='Option for link target')),
                ('page', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='col_obj_metadata', to='lib_collections.CollectionPage')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
    ]
