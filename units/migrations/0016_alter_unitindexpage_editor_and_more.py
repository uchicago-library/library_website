# Generated by Django 4.1.10 on 2023-07-26 16:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("public", "0034_alter_donorpage_content_specialist_and_more"),
        ("staff", "0029_alter_staffindexpage_editor_and_more"),
        ("units", "0015_auto_20220311_1327"),
    ]

    operations = [
        migrations.AlterField(
            model_name="unitindexpage",
            name="editor",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="%(app_label)s_%(class)s_editor",
                to="staff.staffpage",
            ),
        ),
        migrations.AlterField(
            model_name="unitindexpage",
            name="page_maintainer",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="%(app_label)s_%(class)s_maintainer",
                to="staff.staffpage",
            ),
        ),
        migrations.AlterField(
            model_name="unitpage",
            name="editor",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="%(app_label)s_%(class)s_editor",
                to="staff.staffpage",
            ),
        ),
        migrations.AlterField(
            model_name="unitpage",
            name="location",
            field=models.ForeignKey(
                blank=True,
                help_text="Controls the address, hours and quick numbers that will                    appear on various web pages.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="%(app_label)s_%(class)s_related",
                to="public.locationpage",
            ),
        ),
        migrations.AlterField(
            model_name="unitpage",
            name="page_maintainer",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="%(app_label)s_%(class)s_maintainer",
                to="staff.staffpage",
            ),
        ),
    ]