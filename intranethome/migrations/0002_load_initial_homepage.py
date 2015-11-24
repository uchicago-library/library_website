# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.db import migrations

def create_homepage(apps, schema_editor):
    IntranetHomePage = apps.get_model('intranethome.IntranetHomePage')
    intranethome_content_type = apps.get_model('contenttypes.ContentType').objects.get(model='intranethomepage', app_label='intranethome')

    IntranetHomePage.objects.create(
        title="Loop",
        slug='',
        content_type=intranethome_content_type,
        path='00010002',
        depth=2,
        numchild=0,
        url_path='/',
    )

def remove_homepage(apps, schema_editor):
    IntranetHomePage = apps.get_model('intranethome.IntranetHomePage')
    try:
        IntranetHomePage.objects.all()[0].delete()
    except IndexError:
        pass

class Migration(migrations.Migration):
    dependencies = [
        ('intranethome', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_homepage, remove_homepage),
    ]

