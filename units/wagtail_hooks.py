from django.urls import re_path, reverse
from wagtail import hooks
from wagtail.admin.menu import MenuItem

from .views import unit_reporting_admin_view


@hooks.register('register_admin_urls')
def urlconf_time():
    return [
        re_path(
            r'^list_units_wagtail/$',
            unit_reporting_admin_view,
            name='list_units_wagtail',
        )
    ]


@hooks.register('register_settings_menu_item')
def register_frank_menu_item():
    return MenuItem(
        'Unit Reporting',
        reverse('list_units_wagtail'),
        classname='icon icon-mail',
        order=9999,
    )
