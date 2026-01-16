"""
API views for the MyLib Dashboard.

All views return JSON responses for consumption by the React frontend.
"""

from django.http import JsonResponse

from .utils import get_current_cnetid


def require_cnetid(view_func):
    """
    Decorator that ensures the user has a valid CNetID.
    Returns 401 if not authenticated.
    """

    def wrapper(request, *args, **kwargs):
        cnetid = get_current_cnetid(request)
        if not cnetid:
            return JsonResponse({"error": "Authentication required"}, status=401)
        # Add cnetid to request for use in view
        request.cnetid = cnetid
        return view_func(request, *args, **kwargs)

    return wrapper


@require_cnetid
def profile(request):
    """
    Get user profile information.
    Returns: name, email, department, account status
    """
    # TODO: Implement in Step 2 with FOLIO service
    return JsonResponse(
        {"cnetid": request.cnetid, "message": "Profile endpoint - not yet implemented"}
    )


@require_cnetid
def loans(request):
    """
    Get user's checked out items (loans).
    Returns: standardLoans, shortTermLoans arrays with status flags
    """
    # TODO: Implement in Step 3 with FOLIO service
    return JsonResponse(
        {
            "standardLoans": [],
            "shortTermLoans": [],
            "message": "Loans endpoint - not yet implemented",
        }
    )


@require_cnetid
def holds(request):
    """
    Get user's items available for pickup.
    Returns: holds array with pickup locations and deadlines
    """
    # TODO: Implement in Step 4 with FOLIO service
    return JsonResponse(
        {"holds": [], "message": "Holds endpoint - not yet implemented"}
    )


@require_cnetid
def fines(request):
    """
    Get user's fines and fees.
    Returns: total amount and list of fines
    """
    # TODO: Implement in Step 4 with FOLIO service
    return JsonResponse(
        {"total": 0, "fines": [], "message": "Fines endpoint - not yet implemented"}
    )


@require_cnetid
def account_blocks(request):
    """
    Get user's account blocks.
    Returns: list of block messages if any
    """
    # TODO: Implement in Step 4 with FOLIO service
    return JsonResponse(
        {
            "blocks": [],
            "hasBlocks": False,
            "message": "Account blocks endpoint - not yet implemented",
        }
    )
