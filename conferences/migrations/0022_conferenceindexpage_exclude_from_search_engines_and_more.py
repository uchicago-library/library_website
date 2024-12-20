# Generated by Django 4.1.13 on 2024-06-07 18:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("conferences", "0021_alter_conferenceindexpage_news_feed_source_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="conferenceindexpage",
            name="exclude_from_search_engines",
            field=models.BooleanField(
                default=False,
                help_text="Tells search engines not to index the page with a meta robots noindex tag",
            ),
        ),
        migrations.AddField(
            model_name="conferenceindexpage",
            name="exclude_from_site_search",
            field=models.BooleanField(
                default=False, help_text="Excludes the page from the public site search"
            ),
        ),
        migrations.AddField(
            model_name="conferenceindexpage",
            name="exclude_from_sitemap_xml",
            field=models.BooleanField(
                default=False, help_text="Excludes the page from the Google sitemap.xml"
            ),
        ),
        migrations.AddField(
            model_name="conferencepage",
            name="exclude_from_search_engines",
            field=models.BooleanField(
                default=False,
                help_text="Tells search engines not to index the page with a meta robots noindex tag",
            ),
        ),
        migrations.AddField(
            model_name="conferencepage",
            name="exclude_from_site_search",
            field=models.BooleanField(
                default=False, help_text="Excludes the page from the public site search"
            ),
        ),
        migrations.AddField(
            model_name="conferencepage",
            name="exclude_from_sitemap_xml",
            field=models.BooleanField(
                default=False, help_text="Excludes the page from the Google sitemap.xml"
            ),
        ),
        migrations.AddField(
            model_name="conferencesubpage",
            name="exclude_from_search_engines",
            field=models.BooleanField(
                default=False,
                help_text="Tells search engines not to index the page with a meta robots noindex tag",
            ),
        ),
        migrations.AddField(
            model_name="conferencesubpage",
            name="exclude_from_site_search",
            field=models.BooleanField(
                default=False, help_text="Excludes the page from the public site search"
            ),
        ),
        migrations.AddField(
            model_name="conferencesubpage",
            name="exclude_from_sitemap_xml",
            field=models.BooleanField(
                default=False, help_text="Excludes the page from the Google sitemap.xml"
            ),
        ),
    ]
