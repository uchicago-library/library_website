# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from base.models import get_available_path_under, make_slug
from django.apps import apps
from group.models import GroupPage, GroupMeetingMinutesPage, GroupReportsPage
from intranetunits.models import IntranetUnitsPage, IntranetUnitsReportsPage

import base64
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'library_website.settings'

group_meeting_minutes_content_type = apps.get_model('contenttypes.ContentType').objects.get(model='groupmeetingminutespage', app_label='group')
group_reports_content_type = apps.get_model('contenttypes.ContentType').objects.get(model='groupreportspage', app_label='group')
intranet_units_reports_content_type = apps.get_model('contenttypes.ContentType').objects.get(model='intranetunitsreportspage', app_label='intranetunits')

for g in GroupPage.objects.all():
    next_available_path = get_available_path_under(g.path)
    title = "Meeting Minutes"
    GroupMeetingMinutesPage.objects.create(
        title=title,
        slug=make_slug(title),
        content_type=group_meeting_minutes_content_type,
        path=next_available_path,
        depth=g.depth + 1,
        numchild=0,
        url_path=g.url + make_slug(title) + '/'
    )

    next_available_path = get_available_path_under(g.path)
    title = "Reports"
    GroupReportsPage.objects.create(
        title=title,
        slug=make_slug(title),
        content_type=group_reports_content_type,
        path=next_available_path,
        depth=g.depth + 1,
        numchild=0,
        url_path=g.url + make_slug(title) + '/'
    )

for u in IntranetUnitsPage.objects.all():
    next_available_path = get_available_path_under(u.path)
    title = "Reports"
    IntranetUnitsReportsPage.objects.create(
        title=title,
        slug=make_slug(title),
        content_type=intranet_units_reports_content_type,
        path=next_available_path,
        depth=u.depth + 1,
        numchild=0,
        url_path=g.url + make_slug(title) + '/'
    )
    
     
