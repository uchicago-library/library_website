"""
FOLIO API Service for MyLib Dashboard.

Handles authentication and user data retrieval from FOLIO.
Uses the shared get_auth() from item_servlet with dashboard-specific configuration.
"""

import logging

import requests
from django.conf import settings

from item_servlet.utils import FOLIOAuthError, get_auth

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 30


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

        return {
            "id": user.get("id"),
            "firstName": first_name,
            "lastName": personal.get("lastName", ""),
            "email": personal.get("email", ""),
            "department": department,
            "active": user.get("active", False),
            "expirationDate": user.get("expirationDate"),
            "patronGroup": user.get("patronGroup"),
        }

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


# Module-level instance for convenience
_folio_service = None


def get_folio_service():
    """Get or create the FOLIO service singleton."""
    global _folio_service
    if _folio_service is None:
        _folio_service = FOLIOService()
    return _folio_service
