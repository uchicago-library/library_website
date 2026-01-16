"""
Utility functions for the MyLib Dashboard app.
"""

from django.conf import settings


def get_current_cnetid(request):
    """
    Get the current user's CNetID from the request.

    This abstraction allows easy swapping between authentication sources:
    - Dev mode: Returns MYLIB_DEV_USERNAME from settings (for local testing)
    - Production: Returns CNetID from Shibboleth/Okta attributes

    Note: Dashboard users authenticate via Shibboleth at the server level
    but do NOT have Django User records. The CNetID comes from Shibboleth
    attributes in request.META, not from request.user.

    Args:
        request: Django HttpRequest object

    Returns:
        str: The user's CNetID, or None if not authenticated
    """
    # Dev mode: use configured test username
    dev_username = getattr(settings, "MYLIB_DEV_USERNAME", None)
    if dev_username and settings.DEBUG:
        return dev_username

    # Production: get CNetID from Shibboleth attributes
    # Based on SHIBBOLETH_ATTRIBUTE_MAP, 'uid' contains the CNetID
    # Check common ways Shibboleth attributes appear in request.META
    cnetid = (
        request.META.get("uid")
        or request.META.get("HTTP_UID")
        or request.META.get("REMOTE_USER")
        or request.META.get("HTTP_REMOTE_USER")
    )

    return cnetid
