# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.db import migrations

def create_homepage(apps, schema_editor):
    IntranetHomePage = apps.get_model('intranethome.IntranetHomePage')
    intranethome_content_type = apps.get_model('contenttypes.ContentType').objects.get(model='intranethomepage', app_label='intranethome')
   
    # Find the next available second level path- e.g. "00010002".
    # assume that there is a root page with a path of "0001".
    second_level_pages = filter(lambda s: s.path.startswith('0001') and len(s.path) == 8, apps.get_model('wagtailcore.Page').objects.all())
    second_level_paths = sorted(map(lambda p: p.path, second_level_pages))

    i = 0
    while True:
        if i >= len(second_level_paths):
            break
        if not "0001%04d" % (i + 1) == second_level_paths[i]:
            break
        i = i + 1
    next_second_level_path = "0001%04d" % (i + 1)

    IntranetHomePage.objects.create(
        title="Loop",
        slug='',
        content_type=intranethome_content_type,
        path=next_second_level_path,
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

