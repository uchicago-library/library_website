from django.utils.html import format_html
from django.conf import settings
from wagtail.wagtailcore import hooks
from django.shortcuts import redirect
from library_website.settings.base import PERMISSIONS_MAPPING, NO_PERMISSIONS_REDIRECT_URL
from django.contrib.staticfiles.templatetags.staticfiles import static 

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
    if page.id in PERMISSIONS_MAPPING :
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
    return format_html('<link rel="stylesheet" href="' \
    + settings.STATIC_URL \
    + 'css/editor.scss">')


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
    return format_html('<link rel="stylesheet" href="{}">', static('css/admin.css'))
