# Generated by Django 3.0.7 on 2021-02-08 19:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0046_auto_20200807_1121'),
    ]

    operations = [
        migrations.AddField(
            model_name='collectionpage',
            name='citation_config',
            field=models.TextField(default='base=http://ark.lib.uchicago.edu/ark:/61001\n\n[dc]\n\turi=http://purl.org/dc/elements/1.1/\n\ttype=type\n\tidentifier=id\n\tlanguage=language\n\tcreator=author\n\tformat=medium\n\tpublisher=publisher\n\ttitle=title\n[dcterms]\n\turi=http://purl.org/dc/terms/\n\tissued=issued\n\tisPartOf=collection-title\n[bf]\n\turi=http://id.loc.gov/ontologies/bibframe/\n\tClassificationLcc=call-number\n\tDoi=DOI\n\tplace=pubisher-place\n\tscale=scale', help_text='INI-style configuration for Citation service, saying which metadata fields to pull from the Turtle data on the object; see https://github.com/uchicago-library/uchicago-library.github.io for more info', verbose_name='Citation Configuration'),
        ),
    ]