import sys
from io import StringIO

from django.conf import settings
from django.conf.urls import url
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core import management
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.html import format_html
from wagtail.admin.menu import MenuItem
from wagtail.core import hooks

from library_website.settings.base import (
    NO_PERMISSIONS_REDIRECT_URL, PERMISSIONS_MAPPING
)


def get_required_groups(page):
    """
    Get the required groups necessary for a user
    to see a given page.

    Args:
        page: object

    Returns:
        a set of groups of which the user must be
        a member of in order to see the page.
    """
    perms = []
    if page.id in PERMISSIONS_MAPPING:
        perms += PERMISSIONS_MAPPING[page.id]
    else:
        for ancestor in page.get_ancestors():
            if ancestor.id in PERMISSIONS_MAPPING:
                perms += PERMISSIONS_MAPPING[ancestor.id]

    return set(perms)


def has_permission(user, required_groups):
    """
    Determine if a user is a member of the proper
    groups to see a given page.

    Args:
        user: object

    Returns:
        boolean
    """
    user_groups = set([g.name for g in user.groups.all()])
    return user_groups.issuperset(required_groups)


@hooks.register('insert_editor_css')
def editor_css():
    """
    Modify the admin css in order to hide
    option in the rich text editor etc.
    """
    return format_html(
        '<link rel="stylesheet" href="' + settings.STATIC_URL +
        'css/editor.css">'
    )


@hooks.register('before_serve_page')
def redirect_users_without_permissions(page, request, serve_args, serve_kwargs):
    """
    Redirect users of a site if they do not have
    group permission to see a given node.
    """
    if not has_permission(request.user, get_required_groups(page)):
        return redirect(NO_PERMISSIONS_REDIRECT_URL)


@hooks.register('insert_global_admin_css')
def global_admin_css():
    """
    Override the main admin css.
    """
    return format_html(
        '<link rel="stylesheet" href="{}">', static('css/admin.css')
    )


def admin_view(request):
    """
    View for the page owner's report form.
    """
    from base.forms import PageOwnersForm
    if request.method == 'POST':
        form = PageOwnersForm(request.POST)
        options = {
            'site': form.data.get('site', None),
            'cnetid': form.data.get('cnetid', None),
            'role': form.data.get('role', None),
        }
        if form.is_valid():
            # Setup the environment
            backup = sys.stdout

            # Capture stdout
            sys.stdout = StringIO()
            management.call_command(
                'report_page_maintainers_and_editors', **options
            )
            output = sys.stdout.getvalue()

            # Create the HttpResponse object with the appropriate CSV header
            # and append stdout.
            response = HttpResponse(output, content_type='text/csv')
            response['Content-Disposition'
                     ] = 'attachment; filename="page-owner-report.csv"'

            # Restore original stdout
            sys.stdout.close()
            sys.stdout = backup

            return response
    else:
        form = PageOwnersForm()
        return render(request, 'base/page_owners_form.html', {'form': form})


@hooks.register('register_admin_urls')
def urlconf_time():
    return [
        url(r'^page_owners_report/$', admin_view, name='page_owners_report')
    ]


@hooks.register('register_settings_menu_item')
def register_frank_menu_item():
    return MenuItem(
        'Page Owners Report',
        reverse('page_owners_report'),
        classnames='icon icon-download',
        order=10009
    )
