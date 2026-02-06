"""
API views for the MyLib Dashboard.

All views return JSON responses for consumption by the React frontend.
"""

import logging

from django.http import JsonResponse

from .services.aeon import AeonError, get_aeon_service
from .services.folio import FOLIOError, FOLIOUserNotFoundError, get_folio_service
from .services.illiad import ILLiadError, get_illiad_service
from .services.libcal import LibCalError, get_libcal_service
from .utils import get_current_cnetid, get_current_email

logger = logging.getLogger(__name__)


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


def require_email(view_func):
    """
    Decorator that ensures the user has a valid email from authentication.
    Returns 400 if email is not available.

    Should be used after @require_cnetid for ILLiad views that need email.
    """

    def wrapper(request, *args, **kwargs):
        email = get_current_email(request)
        if not email:
            logger.warning(
                f"Email not available for user: {getattr(request, 'cnetid', 'unknown')}"
            )
            return JsonResponse(
                {"error": "Email address not available from authentication"}, status=400
            )
        # Add email to request for use in view
        request.email = email
        return view_func(request, *args, **kwargs)

    return wrapper


@require_cnetid
def profile(request):
    """
    Get user profile information.
    Returns: name, email, department, account status
    """
    try:
        folio = get_folio_service()
        profile_data = folio.get_user_profile(request.cnetid)
        return JsonResponse(profile_data)
    except FOLIOUserNotFoundError:
        logger.warning(f"User not found in FOLIO: {request.cnetid}")
        return JsonResponse({"error": "User not found in library system"}, status=404)
    except FOLIOError as e:
        logger.error(f"FOLIO error for user {request.cnetid}: {e}")
        return JsonResponse(
            {"error": "Unable to retrieve profile information"}, status=503
        )


@require_cnetid
def loans(request):
    """
    Get user's checked out items (loans).
    Returns: standardLoans, shortTermLoans arrays with status flags
    """
    try:
        folio = get_folio_service()
        loans_data = folio.get_user_loans_categorized(request.cnetid)
        return JsonResponse(loans_data)
    except FOLIOUserNotFoundError:
        logger.warning(f"User not found in FOLIO: {request.cnetid}")
        return JsonResponse({"error": "User not found in library system"}, status=404)
    except FOLIOError as e:
        logger.error(f"FOLIO error fetching loans for {request.cnetid}: {e}")
        return JsonResponse(
            {"error": "Unable to retrieve loan information"}, status=503
        )


@require_cnetid
def holds(request):
    """
    Get user's items available for pickup.
    Returns: holds array with pickup locations and deadlines
    """
    try:
        folio = get_folio_service()
        holds_data = folio.get_user_holds(request.cnetid)
        return JsonResponse(holds_data)
    except FOLIOUserNotFoundError:
        logger.warning(f"User not found in FOLIO: {request.cnetid}")
        return JsonResponse({"error": "User not found in library system"}, status=404)
    except FOLIOError as e:
        logger.error(f"FOLIO error fetching holds for {request.cnetid}: {e}")
        return JsonResponse(
            {"error": "Unable to retrieve holds information"}, status=503
        )


@require_cnetid
def fines(request):
    """
    Get user's fines and fees.
    Returns: total amount and list of fines
    """
    try:
        folio = get_folio_service()
        fines_data = folio.get_user_fines(request.cnetid)
        return JsonResponse(fines_data)
    except FOLIOUserNotFoundError:
        logger.warning(f"User not found in FOLIO: {request.cnetid}")
        return JsonResponse({"error": "User not found in library system"}, status=404)
    except FOLIOError as e:
        logger.error(f"FOLIO error fetching fines for {request.cnetid}: {e}")
        return JsonResponse(
            {"error": "Unable to retrieve fines information"}, status=503
        )


@require_cnetid
def account_blocks(request):
    """
    Get user's account blocks.
    Returns: list of block messages if any
    """
    try:
        folio = get_folio_service()
        blocks_data = folio.get_user_blocks(request.cnetid)
        return JsonResponse(blocks_data)
    except FOLIOUserNotFoundError:
        logger.warning(f"User not found in FOLIO: {request.cnetid}")
        return JsonResponse({"error": "User not found in library system"}, status=404)
    except FOLIOError as e:
        logger.error(f"FOLIO error fetching blocks for {request.cnetid}: {e}")
        return JsonResponse({"error": "Unable to retrieve account blocks"}, status=503)


# ILLiad views
# Note: ILLiad uses email addresses as usernames. Email is obtained from
# authentication attributes (Shibboleth/Okta), not from FOLIO, so ILLiad
# integration works independently of the ILS.


@require_cnetid
@require_email
def downloads(request):
    """
    Get electronic copies ready for download (ILL articles and Scan & Deliver).
    Returns: copies array with download URLs
    """
    try:
        illiad = get_illiad_service()
        copies_data = illiad.get_copies_ready(request.email)
        return JsonResponse(copies_data)
    except ILLiadError as e:
        logger.error(f"ILLiad error fetching downloads for {request.cnetid}: {e}")
        return JsonResponse(
            {"error": "Unable to retrieve download information"}, status=503
        )


@require_cnetid
@require_email
def ill_in_process(request):
    """
    Get ILL requests in process (physical items from other libraries).
    Returns: requests array with status
    """
    try:
        illiad = get_illiad_service()
        requests_data = illiad.get_ill_in_process(request.email)
        return JsonResponse(requests_data)
    except ILLiadError as e:
        logger.error(f"ILLiad error fetching ILL requests for {request.cnetid}: {e}")
        return JsonResponse(
            {"error": "Unable to retrieve ILL request information"}, status=503
        )


@require_cnetid
@require_email
def scan_deliver_in_process(request):
    """
    Get Scan & Deliver requests in process.
    Returns: requests array with status
    """
    try:
        illiad = get_illiad_service()
        requests_data = illiad.get_scan_deliver_in_process(request.email)
        return JsonResponse(requests_data)
    except ILLiadError as e:
        logger.error(
            f"ILLiad error fetching Scan & Deliver requests for {request.cnetid}: {e}"
        )
        return JsonResponse(
            {"error": "Unable to retrieve Scan & Deliver information"}, status=503
        )


# LibCal views
# Note: LibCal uses email addresses for filtering bookings. Email is obtained from
# authentication attributes (Shibboleth/Okta).


@require_email
def reservations(request):
    """
    Get user's room reservations (excluding Special Collections).
    Returns: reservations array with room name, times, etc.
    """
    try:
        libcal = get_libcal_service()
        reservations_data = libcal.get_room_reservations(request.email)
        return JsonResponse(reservations_data)
    except LibCalError as e:
        logger.error(f"LibCal error fetching reservations for {request.email}: {e}")
        return JsonResponse(
            {"error": "Unable to retrieve room reservations"}, status=503
        )


@require_email
def sc_seats(request):
    """
    Get user's Special Collections reading room seat reservations.
    Returns: reservations array with room name, times, etc.
    """
    try:
        libcal = get_libcal_service()
        reservations_data = libcal.get_special_collections_seats(request.email)
        return JsonResponse(reservations_data)
    except LibCalError as e:
        logger.error(f"LibCal error fetching SC seats for {request.email}: {e}")
        return JsonResponse(
            {"error": "Unable to retrieve Special Collections reservations"}, status=503
        )


@require_cnetid
def paging_requests(request):
    """
    Get user's paging requests (items being retrieved from stacks/storage).
    Returns: requests array with title, location, status
    """
    try:
        folio = get_folio_service()
        requests_data = folio.get_paging_requests(request.cnetid)
        return JsonResponse(requests_data)
    except FOLIOUserNotFoundError:
        logger.warning(f"User not found in FOLIO: {request.cnetid}")
        return JsonResponse({"error": "User not found in library system"}, status=404)
    except FOLIOError as e:
        logger.error(f"FOLIO error fetching paging requests for {request.cnetid}: {e}")
        return JsonResponse({"error": "Unable to retrieve paging requests"}, status=503)


# Aeon views
# Note: Aeon uses email addresses as usernames. Email is obtained from
# authentication attributes (Shibboleth/Okta).


@require_email
def sc_materials(request):
    """
    Get user's Special Collections material requests from Aeon.
    Returns: requests array with title, call number, scheduled date, status
    """
    try:
        aeon = get_aeon_service()
        materials_data = aeon.get_user_requests(request.email)
        return JsonResponse(materials_data)
    except AeonError as e:
        logger.error(f"Aeon error fetching SC materials for {request.email}: {e}")
        return JsonResponse(
            {"error": "Unable to retrieve Special Collections requests"}, status=503
        )
