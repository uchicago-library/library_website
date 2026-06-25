"""
Wagtail hooks for MyLib Dashboard.
"""

from wagtail import hooks


MYLIB_API_PATH_PREFIX = "/api/mylib/"


@hooks.register("is_request_cacheable")
def skip_mylib_api_cache(request, is_cacheable):
    """
    MyLib API responses vary by Shibboleth identity, not Django auth state.

    wagtail-cache skips Django-authenticated users, but MyLib patrons are
    identified by server-provided Shibboleth attributes in request.META. Bypass
    the Wagtail cache for these API requests so cached responses cannot be
    replayed across patrons.
    """
    path = getattr(request, "path_info", request.path)
    if path.startswith(MYLIB_API_PATH_PREFIX):
        return False

    return is_cacheable
