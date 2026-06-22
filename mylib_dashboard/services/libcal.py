"""
LibCal API Service for MyLib Dashboard.

Handles room reservations, Special Collections reading room seats,
and appointment data retrieval.
"""

import logging
from functools import lru_cache

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 30


class LibCalError(Exception):
    """Base exception for LibCal API errors."""

    pass


class LibCalAuthError(LibCalError):
    """Exception for LibCal authentication failures."""

    pass


class LibCalService:
    """
    Service for interacting with the LibCal (Springshare) API.
    Uses OAuth 2.0 with Client Credentials grant type.
    """

    TOKEN_CACHE_KEY = "libcal_access_token"
    # Cache token for 55 minutes (token expires in 60 minutes)
    TOKEN_CACHE_TTL = 55 * 60

    APPOINTMENT_USERS_CACHE_KEY = "libcal_appointment_users"
    # Cache appointment users for 24 hours
    APPOINTMENT_USERS_CACHE_TTL = 24 * 60 * 60

    def __init__(self):
        self.base_url = getattr(settings, "LIBCAL_API_BASE_URL", "").rstrip("/")
        self.client_id = getattr(settings, "LIBCAL_CLIENT_ID", "")
        self.client_secret = getattr(settings, "LIBCAL_CLIENT_SECRET", "")
        self.timeout = getattr(settings, "LIBCAL_TIMEOUT", DEFAULT_TIMEOUT)
        self.sc_location_ids = getattr(
            settings, "LIBCAL_SPECIAL_COLLECTIONS_LOCATION_IDS", []
        )

    def _get_access_token(self):
        """
        Get a valid access token, fetching a new one if needed.

        Returns:
            str: The access token

        Raises:
            LibCalAuthError: If authentication fails
        """
        # Check cache first
        cached_token = cache.get(self.TOKEN_CACHE_KEY)
        if cached_token:
            return cached_token

        # Fetch new token
        token_url = f"{self.base_url}/oauth/token"

        try:
            response = requests.post(
                token_url,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "client_credentials",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()

            access_token = data.get("access_token")
            if not access_token:
                raise LibCalAuthError("No access token in response")

            # Cache the token
            cache.set(self.TOKEN_CACHE_KEY, access_token, self.TOKEN_CACHE_TTL)

            return access_token

        except requests.exceptions.Timeout:
            logger.error("LibCal token request timed out")
            raise LibCalAuthError("LibCal authentication timed out")
        except requests.exceptions.HTTPError as e:
            logger.error(f"LibCal authentication failed: {e}")
            raise LibCalAuthError(
                f"LibCal authentication failed: {e.response.status_code}"
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"LibCal authentication error: {e}")
            raise LibCalAuthError(f"LibCal authentication failed: {e}")

    def _request(self, endpoint, params=None):
        """
        Make an authenticated GET request to LibCal.

        Args:
            endpoint: API endpoint (without base URL)
            params: Optional query parameters

        Returns:
            list or dict: JSON response

        Raises:
            LibCalError: If the request fails
        """
        url = f"{self.base_url}{endpoint}"
        access_token = self._get_access_token()

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }

        try:
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            logger.error(f"LibCal request timed out: {endpoint}")
            raise LibCalError("Request to LibCal timed out")
        except requests.exceptions.HTTPError as e:
            logger.error(f"LibCal request failed: {endpoint} - {e}")
            raise LibCalError(f"LibCal request failed: {e.response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"LibCal request error: {endpoint} - {e}")
            raise LibCalError(f"LibCal request failed: {e}")

    def _format_booking(self, booking):
        """
        Format a booking for the frontend.

        Args:
            booking: The booking object from LibCal

        Returns:
            dict: Formatted booking data
        """
        return {
            "id": str(booking.get("id", "")),
            "bookId": booking.get("bookId", ""),
            "roomName": booking.get("item_name", ""),
            "locationName": booking.get("location_name", ""),
            "categoryName": booking.get("category_name", ""),
            "locationId": booking.get("lid"),
            "startTime": booking.get("fromDate", ""),
            "endTime": booking.get("toDate", ""),
            "status": booking.get("status", ""),
            "nickname": booking.get("nickname", ""),
            "checkInCode": booking.get("check_in_code", ""),
        }

    def get_bookings(self, email, days=7):
        """
        Get all bookings for a user by email.

        Results are cached for 60 seconds to avoid duplicate API calls
        when multiple views (reservations, sc_seats) need the same data.

        Args:
            email: The user's email address
            days: Number of days to look ahead (required by API, default 7)

        Returns:
            list: List of booking objects
        """
        cache_key = f"libcal_bookings_{email}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        endpoint = "/space/bookings"
        params = {"email": email, "days": days}

        bookings = self._request(endpoint, params)

        # Ensure we have a list
        if not isinstance(bookings, list):
            logger.warning(f"Unexpected LibCal response type: {type(bookings)}")
            return []

        cache.set(cache_key, bookings, 60)
        return bookings

    def get_room_reservations(self, email):
        """
        Get room reservations for a user (excluding Special Collections).

        Args:
            email: The user's email address

        Returns:
            dict: {
                "reservations": [...],
                "totalReservations": int,
            }
        """
        bookings = self.get_bookings(email)

        # Filter out Special Collections locations (using 'lid' field)
        room_bookings = [
            b for b in bookings if b.get("lid") not in self.sc_location_ids
        ]

        # Format and sort by start time
        reservations = [self._format_booking(b) for b in room_bookings]
        reservations.sort(key=lambda r: r.get("startTime") or "")

        return {
            "reservations": reservations,
            "totalReservations": len(reservations),
        }

    def get_special_collections_seats(self, email):
        """
        Get Special Collections reading room seat reservations for a user.

        Args:
            email: The user's email address

        Returns:
            dict: {
                "reservations": [...],
                "totalReservations": int,
            }
        """
        bookings = self.get_bookings(email)

        # Filter for Special Collections locations only (using 'lid' field)
        sc_bookings = [b for b in bookings if b.get("lid") in self.sc_location_ids]

        # Format and sort by start time
        reservations = [self._format_booking(b) for b in sc_bookings]
        reservations.sort(key=lambda r: r.get("startTime") or "")

        return {
            "reservations": reservations,
            "totalReservations": len(reservations),
        }

    def get_appointment_users(self):
        """
        Fetch appointment users (librarians) from LibCal.

        Results are cached for 24 hours since librarian info rarely changes.

        Returns:
            dict: Mapping of userId (int) → {firstName, lastName, email}
        """
        cached = cache.get(self.APPOINTMENT_USERS_CACHE_KEY)
        if cached is not None:
            return cached

        data = self._request("/appointments/users")

        # Build lookup dict from the list of user objects
        # API returns snake_case fields: id, first_name, last_name, email
        users = {}
        if isinstance(data, list):
            for user in data:
                user_id = user.get("id")
                if user_id is not None:
                    users[user_id] = {
                        "firstName": user.get("first_name", ""),
                        "lastName": user.get("last_name", ""),
                        "email": user.get("email", ""),
                    }

        cache.set(
            self.APPOINTMENT_USERS_CACHE_KEY, users, self.APPOINTMENT_USERS_CACHE_TTL
        )
        return users

    def _format_appointment(self, appointment, users=None):
        """
        Format an appointment booking for the frontend.

        Args:
            appointment: The appointment object from LibCal
            users: Optional dict of userId → user info for librarian name lookup

        Returns:
            dict: Formatted appointment data
        """
        librarian_name = ""
        user_id = appointment.get("userId")
        if users and user_id in users:
            user = users[user_id]
            first = user.get("firstName", "")
            last = user.get("lastName", "")
            librarian_name = f"{first} {last}".strip()

        return {
            "id": str(appointment.get("id", "")),
            "startTime": appointment.get("fromDate", ""),
            "endTime": appointment.get("toDate", ""),
            "location": appointment.get("location", ""),
            "group": appointment.get("group", ""),
            "directions": appointment.get("directions", ""),
            "librarianName": librarian_name,
        }

    def get_appointments(self, email, days=90):
        """
        Get appointments for a user by email.

        Args:
            email: The user's email address
            days: Number of days to look ahead (default 90)

        Returns:
            dict: {
                "appointments": [...],
                "totalAppointments": int,
            }
        """
        endpoint = "/appointments/bookings"
        params = {
            "email": email,
            "days": days,
            "include_cancellations": 1,
        }

        data = self._request(endpoint, params)

        # Ensure we have a list
        if not isinstance(data, list):
            logger.warning(
                f"Unexpected LibCal appointments response type: {type(data)}"
            )
            data = []

        # Fetch librarian user info for name enrichment
        try:
            users = self.get_appointment_users()
        except LibCalError:
            logger.warning("Could not fetch appointment users for name enrichment")
            users = {}

        # Format and sort by start time
        appointments = [self._format_appointment(a, users) for a in data]
        appointments.sort(key=lambda a: a.get("startTime") or "")

        return {
            "appointments": appointments,
            "totalAppointments": len(appointments),
        }


@lru_cache(maxsize=1)
def get_libcal_service():
    """Get a cached LibCalService instance."""
    return LibCalService()
