# Generated by Django 4.1.13 on 2024-04-25 21:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ask_a_librarian", "0024_alter_askpage_content_specialist_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="askpage",
            name="news_feed_source",
            field=models.CharField(
                blank=True,
                choices=[
                    ("", "--------"),
                    ("library_kiosk", "Library"),
                    ("law_kiosk", "Law"),
                    ("sciences_kiosk", "Sciences"),
                    ("scrc_kiosk", "SCRC"),
                    ("cds_kiosk", "CDS"),
                ],
                default="",
                max_length=50,
            ),
        ),
    ]