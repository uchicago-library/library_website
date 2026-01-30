"""
FOLIO API Service for MyLib Dashboard.

Handles authentication and user data retrieval from FOLIO.
Uses the shared get_auth() from item_servlet with dashboard-specific configuration.
"""

import logging
from datetime import datetime, timedelta, timezone

import requests
from django.conf import settings
from django.core.cache import cache

from item_servlet.utils import FOLIOAuthError, get_auth

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 30

# Hours threshold for "due soon" warning
DUE_SOON_HOURS = 24


class FOLIOError(Exception):
    """Base exception for FOLIO API errors."""

    pass


class FOLIOUserNotFoundError(FOLIOError):
    """Raised when a user is not found in FOLIO."""

    pass


class FOLIOService:
    """
    Service for interacting with the FOLIO API.

    Authenticates fresh each request (no token caching) following
    FOLIO RTR best practices - FOLIO handles token caching on their side.
    """

    def __init__(self):
        self.base_url = getattr(settings, "FOLIO_BASE_URL", "")
        self.tenant = getattr(settings, "FOLIO_TENANT", "")
        self.timeout = getattr(settings, "FOLIO_TIMEOUT", DEFAULT_TIMEOUT)

        # Configure proxies if SOCKS proxy is set (for local development)
        proxy = getattr(settings, "FOLIO_PROXY", None)
        self.proxies = None
        if proxy:
            self.proxies = {
                "http": proxy,
                "https": proxy,
            }

    def _get_headers(self):
        """Build headers for FOLIO API requests (without token)."""
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Okapi-Tenant": self.tenant,
        }

    def _get_token(self):
        """
        Get a FOLIO authentication token.

        Uses the shared get_auth() with dashboard-specific configuration.

        Returns:
            str: The access token

        Raises:
            FOLIOError: If authentication fails
        """
        try:
            auth = get_auth(
                proxies=self.proxies,
                timeout=self.timeout,
                raise_on_error=True,
            )
            return auth["x-okapi-token"]
        except FOLIOAuthError as e:
            raise FOLIOError(str(e))

    def _request(self, method, endpoint, **kwargs):
        """
        Make an authenticated request to FOLIO.

        Authenticates fresh each time (no token caching).

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            **kwargs: Additional arguments passed to requests

        Returns:
            dict: JSON response

        Raises:
            FOLIOError: If the request fails
        """
        token = self._get_token()

        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        headers["X-Okapi-Token"] = token

        # Merge headers with any provided
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        try:
            response = requests.request(
                method,
                url,
                headers=headers,
                proxies=self.proxies,
                timeout=self.timeout,
                **kwargs,
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            logger.error(f"FOLIO request timed out: {endpoint}")
            raise FOLIOError("Request to FOLIO timed out")
        except requests.exceptions.HTTPError as e:
            logger.error(f"FOLIO request failed: {endpoint} - {e}")
            raise FOLIOError(f"FOLIO request failed: {e.response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"FOLIO request error: {endpoint} - {e}")
            raise FOLIOError(f"FOLIO request failed: {e}")

    def get_user_by_cnetid(self, cnetid):
        """
        Look up a user by their CNetID (username).

        Results are cached for 5 minutes to avoid redundant API calls
        when multiple dashboard sections need user data.

        Args:
            cnetid: The user's CNetID

        Returns:
            dict: User data including:
                - id: User UUID
                - firstName: First name
                - lastName: Last name
                - email: Email address
                - department: Department affiliation (from customFields)
                - active: Whether the account is active
                - expirationDate: Account expiration date

        Raises:
            FOLIOUserNotFoundError: If the user is not found
            FOLIOError: If the request fails
        """
        # Check cache first
        cache_key = f"folio_user_{cnetid}"
        cached_user = cache.get(cache_key)
        if cached_user is not None:
            return cached_user

        endpoint = f'/users?query=username=="{cnetid}"'
        data = self._request("GET", endpoint)

        users = data.get("users", [])
        if not users:
            logger.warning(f"User not found in FOLIO: {cnetid}")
            raise FOLIOUserNotFoundError(f"User not found: {cnetid}")

        user = users[0]
        personal = user.get("personal", {})
        custom_fields = user.get("customFields", {})

        # Extract department - try staff first, then student
        department = (
            custom_fields.get("staffDepartment")
            or custom_fields.get("studentDepartment")
            or ""
        )

        # Use preferred name if available
        first_name = personal.get("preferredFirstName") or personal.get("firstName", "")

        user_data = {
            "id": user.get("id"),
            "firstName": first_name,
            "lastName": personal.get("lastName", ""),
            "email": personal.get("email", ""),
            "department": department,
            "active": user.get("active", False),
            "expirationDate": user.get("expirationDate"),
            "patronGroup": user.get("patronGroup"),
        }

        # Cache for 5 minutes
        cache.set(cache_key, user_data, 300)

        return user_data

    def get_user_profile(self, cnetid):
        """
        Get complete user profile data for the dashboard.

        Args:
            cnetid: The user's CNetID

        Returns:
            dict: Profile data formatted for the frontend
        """
        user = self.get_user_by_cnetid(cnetid)

        display_name = f"{user['firstName']} {user['lastName']}".strip()

        return {
            "cnetid": cnetid,
            "uuid": user["id"],
            "displayName": display_name,
            "firstName": user["firstName"],
            "lastName": user["lastName"],
            "email": user["email"],
            "department": user["department"],
            "active": user["active"],
            "expirationDate": user["expirationDate"],
        }

    def get_user_email(self, cnetid):
        """
        Get a user's email address from their CNetID.

        Used for ILLiad lookups which require email instead of CNetID.

        Args:
            cnetid: The user's CNetID

        Returns:
            str: The user's email address

        Raises:
            FOLIOUserNotFoundError: If the user is not found
            FOLIOError: If the request fails
        """
        user = self.get_user_by_cnetid(cnetid)
        return user["email"]

    def get_user_loans(self, user_uuid):
        """
        Get all open loans for a user.

        Args:
            user_uuid: The user's FOLIO UUID

        Returns:
            list: List of loan objects from FOLIO
        """
        endpoint = (
            f"/circulation/loans?query=userId=={user_uuid}"
            f"%20and%20status.name==Open&limit=1000"
        )
        data = self._request("GET", endpoint)
        return data.get("loans", [])

    def _parse_due_date(self, due_date_str):
        """Parse FOLIO due date string to datetime."""
        if not due_date_str:
            return None
        try:
            # FOLIO returns ISO format dates
            return datetime.fromisoformat(due_date_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            logger.warning(f"Could not parse due date: {due_date_str}")
            return None

    def _compute_loan_status(self, loan):
        """
        Compute status flags for a loan.

        Args:
            loan: The loan object from FOLIO

        Returns:
            dict: Status flags (isOverdue, isDueSoon, isRecalled)
        """
        now = datetime.now(timezone.utc)
        due_date = self._parse_due_date(loan.get("dueDate"))

        is_overdue = False
        is_due_soon = False

        if due_date:
            is_overdue = now > due_date
            if not is_overdue:
                due_soon_threshold = now + timedelta(hours=DUE_SOON_HOURS)
                is_due_soon = due_date <= due_soon_threshold

        is_recalled = loan.get("action") == "recallrequested"

        return {
            "isOverdue": is_overdue,
            "isDueSoon": is_due_soon,
            "isRecalled": is_recalled,
        }

    def _format_loan(self, loan, status):
        """
        Format a loan for the frontend.

        Args:
            loan: The loan object from FOLIO
            status: Status flags from _compute_loan_status

        Returns:
            dict: Formatted loan data
        """
        item = loan.get("item", {})

        return {
            "id": loan.get("id"),
            "itemId": loan.get("itemId"),
            "title": item.get("title", "Unknown Title"),
            "author": (
                item.get("contributors", [{}])[0].get("name", "")
                if item.get("contributors")
                else ""
            ),
            "barcode": item.get("barcode", ""),
            "dueDate": loan.get("dueDate"),
            "renewalCount": loan.get("renewalCount", 0),
            "loanPolicyId": loan.get("loanPolicyId"),
            **status,
        }

    def get_user_loans_categorized(self, cnetid):
        """
        Get user's loans categorized as standard or short-term.

        Args:
            cnetid: The user's CNetID

        Returns:
            dict: {
                "standardLoans": [...],
                "shortTermLoans": [...],
                "totalLoans": int,
                "recalledCount": int,
                "overdueCount": int,
                "dueSoonCount": int,
            }
        """
        # Get user UUID first
        user = self.get_user_by_cnetid(cnetid)
        user_uuid = user["id"]

        # Fetch loans
        loans = self.get_user_loans(user_uuid)

        if not loans:
            return {
                "standardLoans": [],
                "shortTermLoans": [],
                "totalLoans": 0,
                "recalledCount": 0,
                "overdueCount": 0,
                "dueSoonCount": 0,
            }

        # Get short-term policy IDs from settings
        short_term_policy_ids = set(
            getattr(settings, "FOLIO_SHORT_TERM_LOAN_POLICY_IDS", [])
        )

        standard_loans = []
        short_term_loans = []
        recalled_count = 0
        overdue_count = 0
        due_soon_count = 0

        for loan in loans:
            # Recall status is embedded in loan.action (no separate API call needed)
            status = self._compute_loan_status(loan)
            formatted_loan = self._format_loan(loan, status)

            # Update counts
            if status["isRecalled"]:
                recalled_count += 1
            if status["isOverdue"]:
                overdue_count += 1
            if status["isDueSoon"]:
                due_soon_count += 1

            # Categorize by policy ID
            loan_policy_id = loan.get("loanPolicyId")
            if short_term_policy_ids and loan_policy_id in short_term_policy_ids:
                short_term_loans.append(formatted_loan)
            else:
                standard_loans.append(formatted_loan)

        # Sort by due date (soonest first)
        standard_loans.sort(key=lambda loan: loan.get("dueDate"))
        short_term_loans.sort(key=lambda loan: loan.get("dueDate"))

        return {
            "standardLoans": standard_loans,
            "shortTermLoans": short_term_loans,
            "totalLoans": len(loans),
            "recalledCount": recalled_count,
            "overdueCount": overdue_count,
            "dueSoonCount": due_soon_count,
        }

    def get_service_points(self):
        """
        Get all service points (pickup locations).

        Returns a dict mapping service point IDs to their names.
        Results are cached in Django's cache for 24 hours.

        Returns:
            dict: {service_point_id: name, ...}
        """
        cache_key = "folio_service_points"
        service_points = cache.get(cache_key)

        if service_points is None:
            endpoint = "/service-points?limit=1000"
            data = self._request("GET", endpoint)
            service_points = {
                sp["id"]: sp.get("discoveryDisplayName") or sp.get("name", "Unknown")
                for sp in data.get("servicepoints", [])
            }
            # Cache for 24 hours
            cache.set(cache_key, service_points, 60 * 60 * 24)

        return service_points

    def get_user_holds(self, cnetid):
        """
        Get items available for pickup for a user.

        Args:
            cnetid: The user's CNetID

        Returns:
            dict: {
                "holds": [...],
                "totalHolds": int,
            }
        """
        user = self.get_user_by_cnetid(cnetid)
        user_uuid = user["id"]

        # Get service points for location name lookup
        service_points = self.get_service_points()

        # Query for requests awaiting pickup
        endpoint = (
            f"/request-storage/requests?query="
            f"(requesterId=={user_uuid}%20or%20proxyUserId=={user_uuid})"
            f"%20and%20status==%22Open%20-%20Awaiting%20pickup%22&limit=1000"
        )
        data = self._request("GET", endpoint)
        requests_list = data.get("requests", [])

        holds = []
        for req in requests_list:
            title = req.get("instance", {}).get("title") or req.get("item", {}).get(
                "title", "Unknown Title"
            )
            pickup_sp_id = req.get("pickupServicePointId")
            holds.append(
                {
                    "id": req.get("id"),
                    "title": title,
                    "requestType": req.get("requestType"),
                    "pickupServicePointId": pickup_sp_id,
                    "pickupLocation": service_points.get(pickup_sp_id, ""),
                    "holdShelfExpirationDate": req.get("holdShelfExpirationDate"),
                    "position": req.get("position"),
                }
            )

        # Sort by expiration date (soonest first)
        holds.sort(key=lambda h: h.get("holdShelfExpirationDate") or "")

        return {
            "holds": holds,
            "totalHolds": len(holds),
        }

    def get_user_fines(self, cnetid):
        """
        Get open fines/fees for a user.

        Args:
            cnetid: The user's CNetID

        Returns:
            dict: {
                "fines": [...],
                "totalAmount": float,
                "totalFines": int,
            }
        """
        user = self.get_user_by_cnetid(cnetid)
        user_uuid = user["id"]

        endpoint = (
            f"/accounts?query=userId=={user_uuid}"
            f"%20and%20status.name==Open&limit=1000"
        )
        data = self._request("GET", endpoint)
        accounts = data.get("accounts", [])

        fines = []
        total_amount = 0.0

        for account in accounts:
            remaining = account.get("remaining", 0)
            total_amount += remaining

            fines.append(
                {
                    "id": account.get("id"),
                    "amount": account.get("amount"),
                    "remaining": remaining,
                    "feeFineType": account.get("feeFineType"),
                    "title": account.get("title", ""),
                    "createdDate": account.get("metadata", {}).get("createdDate"),
                }
            )

        return {
            "fines": fines,
            "totalAmount": total_amount,
            "totalFines": len(fines),
        }

    def get_user_blocks(self, cnetid):
        """
        Get account blocks for a user.

        Args:
            cnetid: The user's CNetID

        Returns:
            dict: {
                "blocks": [...],
                "hasBlocks": bool,
            }
        """
        user = self.get_user_by_cnetid(cnetid)
        user_uuid = user["id"]

        blocks = []

        # Get automated blocks
        try:
            endpoint = f"/automated-patron-blocks/{user_uuid}"
            data = self._request("GET", endpoint)
            for block in data.get("automatedPatronBlocks", []):
                blocks.append(
                    {
                        "type": "automated",
                        "message": block.get("message", "Account has restrictions"),
                        "blockBorrowing": block.get("blockBorrowing", False),
                        "blockRenewals": block.get("blockRenewals", False),
                        "blockRequests": block.get("blockRequests", False),
                    }
                )
        except FOLIOError:
            logger.warning(f"Could not fetch automated blocks for {cnetid}")

        # Get manual blocks
        try:
            endpoint = f"/manualblocks?query=userId=={user_uuid}"
            data = self._request("GET", endpoint)
            for block in data.get("manualblocks", []):
                message = block.get("patronMessage") or block.get(
                    "desc", "Account has restrictions"
                )
                blocks.append(
                    {
                        "type": "manual",
                        "message": message,
                        "blockBorrowing": block.get("borrowing", False),
                        "blockRenewals": block.get("renewals", False),
                        "blockRequests": block.get("requests", False),
                    }
                )
        except FOLIOError:
            logger.warning(f"Could not fetch manual blocks for {cnetid}")

        return {
            "blocks": blocks,
            "hasBlocks": len(blocks) > 0,
        }


# Module-level instance for convenience
_folio_service = None


def get_folio_service():
    """Get or create the FOLIO service singleton."""
    global _folio_service
    if _folio_service is None:
        _folio_service = FOLIOService()
    return _folio_service
