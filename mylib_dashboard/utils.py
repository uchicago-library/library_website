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


def get_current_email(request):
    """
    Get the current user's email address from the request.

    This abstraction allows easy swapping between authentication sources:
    - Dev mode: Returns MYLIB_DEV_EMAIL from settings (for local testing)
    - Production: Returns email from Shibboleth/Okta attributes

    Used primarily for ILLiad integration, which uses email addresses
    as usernames rather than CNetIDs.

    Args:
        request: Django HttpRequest object

    Returns:
        str: The user's email address, or None if not available
    """
    # Dev mode: use configured test email
    dev_email = getattr(settings, "MYLIB_DEV_EMAIL", None)
    if dev_email and settings.DEBUG:
        return dev_email

    # Production: get email from Shibboleth/Okta attributes
    # Check common ways email attributes appear in request.META
    email = (
        request.META.get("mail")
        or request.META.get("HTTP_MAIL")
        or request.META.get("email")
        or request.META.get("HTTP_EMAIL")
        or request.META.get("HTTP_EPPN")  # eduPersonPrincipalName (often email format)
    )

    return email
