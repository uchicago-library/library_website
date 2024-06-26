# Generated by Django 4.1.10 on 2023-07-26 16:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("staff", "0028_alter_staffpage_bio"),
        ("intranetunits", "0014_auto_20220920_1154"),
    ]

    operations = [
        migrations.AlterField(
            model_name="intranetunitsindexpage",
            name="editor",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="%(app_label)s_%(class)s_editor",
                to="staff.staffpage",
            ),
        ),
        migrations.AlterField(
            model_name="intranetunitsindexpage",
            name="page_maintainer",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="%(app_label)s_%(class)s_maintainer",
                to="staff.staffpage",
            ),
        ),
        migrations.AlterField(
            model_name="intranetunitspage",
            name="editor",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="%(app_label)s_%(class)s_editor",
                to="staff.staffpage",
            ),
        ),
        migrations.AlterField(
            model_name="intranetunitspage",
            name="page_maintainer",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="%(app_label)s_%(class)s_maintainer",
                to="staff.staffpage",
            ),
        ),
        migrations.AlterField(
            model_name="intranetunitsreportsindexpage",
            name="editor",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="%(app_label)s_%(class)s_editor",
                to="staff.staffpage",
            ),
        ),
        migrations.AlterField(
            model_name="intranetunitsreportsindexpage",
            name="page_maintainer",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="%(app_label)s_%(class)s_maintainer",
                to="staff.staffpage",
            ),
        ),
        migrations.AlterField(
            model_name="intranetunitsreportspage",
            name="editor",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="%(app_label)s_%(class)s_editor",
                to="staff.staffpage",
            ),
        ),
        migrations.AlterField(
            model_name="intranetunitsreportspage",
            name="page_maintainer",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="%(app_label)s_%(class)s_maintainer",
                to="staff.staffpage",
            ),
        ),
    ]
