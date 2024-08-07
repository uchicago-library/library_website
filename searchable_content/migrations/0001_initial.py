# Generated by Django 2.0.3 on 2018-11-29 21:27

from django.db import migrations, models
import wagtail.search.index


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SearchableContent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text="The page title as you'd like it to be seen by the public", max_length=255, verbose_name='title')),
                ('datestamp', models.CharField(help_text='Datestamp from OAI-PMH', max_length=255, verbose_name='datestamp')),
                ('url', models.CharField(help_text='URL', max_length=255, verbose_name='url')),
                ('description', models.CharField(help_text='Description', max_length=255, verbose_name='description')),
                ('subject', models.CharField(help_text='Subject', max_length=255, verbose_name='subject')),
                ('tag', models.CharField(help_text='A tag for deleting and replacing these objects in bulk.', max_length=255, verbose_name='tag')),
            ],
            bases=(wagtail.search.index.Indexed, models.Model),
        ),
    ]
