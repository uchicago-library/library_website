# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from base.models import get_available_path_under
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from django.db import migrations

def create_homepage(apps, schema_editor):
    IntranetHomePage = apps.get_model('intranethome.IntranetHomePage')
    intranethome_content_type = apps.get_model('contenttypes.ContentType').objects.get(model='intranethomepage', app_label='intranethome')
    next_second_level_path = get_available_path_under("0001")

    intranet_homepage = IntranetHomePage.objects.create(
        title="Loop",
        slug='',
        content_type=intranethome_content_type,
        path=next_second_level_path,
        depth=2,
        numchild=0,
        url_path='/',
    )

    # Create a staffweb site.
    apps.get_model('wagtailcore.Site').objects.create(
        hostname='localhost',
        root_page_id=intranet_homepage.id,
        is_default_site=True
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

