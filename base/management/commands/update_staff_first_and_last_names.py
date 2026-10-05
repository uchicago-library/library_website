# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from staff.models import StaffPage


class Command(BaseCommand):
    """
    Pull first and last name from the User object into StaffPage objects.

    Example:
        python manage.py update_staff_first_and_last_names
    """

    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement this
        method. It may return a Unicode string which will be printed to
        stdout. More: https://docs.djangoproject.com/en/1.8/howto/custom
        -management-commands/#django.core.management.BaseCommand.handle
        """

        output = []
        for s in StaffPage.objects.all():
            try:
                user = User.objects.get(username=s.cnetid)
            except:  # noqa: E722
                continue
            s.first_name = user.first_name
            s.last_name = user.last_name
            s.save()

        return "\n".join(output)
