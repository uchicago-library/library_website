# Generated by Django 2.0.12 on 2019-09-17 21:58

from django.db import migrations
import wagtail.blocks
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('lib_news', '0008_libnewspage_exhibit_story_hours_override'),
    ]

    operations = [
        migrations.AlterField(
            model_name='libnewsindexpage',
            name='navigation',
            field=wagtail.fields.StreamField([('navigation', wagtail.blocks.PageChooserBlock(page_type=['lib_news.LibNewsPage'], required=False))], blank=True, default=[], null=True),
        ),
    ]
