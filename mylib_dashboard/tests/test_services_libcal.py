"""Tests for mylib_dashboard.services.libcal."""

from unittest.mock import MagicMock, patch

import requests as real_requests
from django.core.cache import cache
from django.test import TestCase, override_settings

from mylib_dashboard.services.libcal import (
    LibCalAuthError,
    LibCalError,
    LibCalService,
    get_libcal_service,
)

LIBCAL_SETTINGS = {
    "LIBCAL_API_BASE_URL": "http://libcal.test",
    "LIBCAL_CLIENT_ID": "test-client-id",
    "LIBCAL_CLIENT_SECRET": "test-secret",
    "LIBCAL_TIMEOUT": 10,
    "LIBCAL_SPECIAL_COLLECTIONS_LOCATION_IDS": [100],
}


@override_settings(**LIBCAL_SETTINGS)
class TestLibCalGetAccessToken(TestCase):
    """Tests for LibCalService._get_access_token."""

    @classmethod
    def setUpTestData(cls):
        cls.service = LibCalService()

    def setUp(self):
        cache.clear()

    @patch("mylib_dashboard.services.libcal.requests")
    def test_fetches_new_token(self, mock_requests):
        mock_response = MagicMock()
        mock_response.json.return_value = {"access_token": "new-token-abc"}
        mock_requests.post.return_value = mock_response

        token = self.service._get_access_token()

        self.assertEqual(token, "new-token-abc")
        mock_requests.post.assert_called_once()

    @patch("mylib_dashboard.services.libcal.cache")
    @patch("mylib_dashboard.services.libcal.requests")
    def test_second_call_returns_cached_token(self, mock_requests, mock_cache):
        mock_response = MagicMock()
        mock_response.json.return_value = {"access_token": "fresh-token"}
        mock_requests.post.return_value = mock_response

        # First call: cache miss, fetches from API and caches
        mock_cache.get.return_value = None
        token1 = self.service._get_access_token()

        # Second call: cache hit
        mock_cache.get.return_value = "fresh-token"
        token2 = self.service._get_access_token()

        self.assertEqual(token1, "fresh-token")
        self.assertEqual(token2, "fresh-token")
        mock_requests.post.assert_called_once()
        mock_cache.set.assert_called_once()

    @patch("mylib_dashboard.services.libcal.requests")
    def test_raises_on_missing_access_token(self, mock_requests):
        mock_requests.exceptions = real_requests.exceptions
        mock_response = MagicMock()
        mock_response.json.return_value = {"error": "invalid_client"}
        mock_requests.post.return_value = mock_response

        with self.assertRaises(LibCalAuthError) as ctx:
            self.service._get_access_token()
        self.assertIn("No access token", str(ctx.exception))

    @patch("mylib_dashboard.services.libcal.requests")
    def test_timeout_raises_auth_error(self, mock_requests):
        mock_requests.post.side_effect = real_requests.exceptions.Timeout()
        mock_requests.exceptions = real_requests.exceptions

        with self.assertLogs("mylib_dashboard.services.libcal", level="ERROR"):
            with self.assertRaises(LibCalAuthError) as ctx:
                self.service._get_access_token()
        self.assertIn("timed out", str(ctx.exception))


@override_settings(**LIBCAL_SETTINGS)
class TestLibCalRequest(TestCase):
    """Tests for LibCalService._request."""

    @classmethod
    def setUpTestData(cls):
        cls.service = LibCalService()

    def setUp(self):
        cache.clear()

    @patch.object(LibCalService, "_get_access_token", return_value="test-token")
    @patch("mylib_dashboard.services.libcal.requests")
    def test_successful_request(self, mock_requests, mock_token):
        mock_response = MagicMock()
        mock_response.json.return_value = [{"id": 1}]
        mock_requests.get.return_value = mock_response

        result = self.service._request("/space/bookings")

        self.assertEqual(result, [{"id": 1}])

    @patch.object(LibCalService, "_get_access_token", return_value="tok")
    @patch("mylib_dashboard.services.libcal.requests")
    def test_timeout_raises_error(self, mock_requests, mock_token):

        mock_requests.get.side_effect = real_requests.exceptions.Timeout()
        mock_requests.exceptions = real_requests.exceptions

        with self.assertLogs("mylib_dashboard.services.libcal", level="ERROR"):
            with self.assertRaises(LibCalError) as ctx:
                self.service._request("/test")
        self.assertIn("timed out", str(ctx.exception))

    @patch.object(LibCalService, "_get_access_token", return_value="tok")
    @patch("mylib_dashboard.services.libcal.requests")
    def test_http_error_raises_error(self, mock_requests, mock_token):

        mock_resp = MagicMock()
        mock_resp.status_code = 403
        mock_requests.get.side_effect = real_requests.exceptions.HTTPError(
            response=mock_resp
        )
        mock_requests.exceptions = real_requests.exceptions

        with self.assertLogs("mylib_dashboard.services.libcal", level="ERROR"):
            with self.assertRaises(LibCalError) as ctx:
                self.service._request("/test")
        self.assertIn("403", str(ctx.exception))

    @patch.object(LibCalService, "_get_access_token", return_value="tok")
    @patch("mylib_dashboard.services.libcal.requests")
    def test_request_exception_raises_error(self, mock_requests, mock_token):

        mock_requests.get.side_effect = real_requests.exceptions.ConnectionError("fail")
        mock_requests.exceptions = real_requests.exceptions

        with self.assertLogs("mylib_dashboard.services.libcal", level="ERROR"):
            with self.assertRaises(LibCalError):
                self.service._request("/test")


@override_settings(**LIBCAL_SETTINGS)
class TestFormatBooking(TestCase):
    """Tests for LibCalService._format_booking."""

    @classmethod
    def setUpTestData(cls):
        cls.service = LibCalService()

    def test_formats_booking(self):
        booking = {
            "id": 5001,
            "bookId": "bk-1",
            "item_name": "Study Room 201",
            "location_name": "Regenstein Library",
            "category_name": "Study Rooms",
            "lid": 50,
            "fromDate": "2026-03-15T10:00:00",
            "toDate": "2026-03-15T12:00:00",
            "status": "Confirmed",
            "nickname": "My Study Session",
            "check_in_code": "ABC123",
        }

        result = self.service._format_booking(booking)

        self.assertEqual(result["id"], "5001")
        self.assertEqual(result["roomName"], "Study Room 201")
        self.assertEqual(result["locationName"], "Regenstein Library")
        self.assertEqual(result["startTime"], "2026-03-15T10:00:00")
        self.assertEqual(result["endTime"], "2026-03-15T12:00:00")
        self.assertEqual(result["checkInCode"], "ABC123")


@override_settings(**LIBCAL_SETTINGS)
class TestGetBookings(TestCase):
    """Tests for LibCalService.get_bookings."""

    @classmethod
    def setUpTestData(cls):
        cls.service = LibCalService()

    def setUp(self):
        cache.clear()

    @patch("mylib_dashboard.services.libcal.cache")
    @patch.object(LibCalService, "_request")
    def test_fetches_and_caches_bookings(self, mock_request, mock_cache):
        mock_request.return_value = [
            {"id": 1, "item_name": "Room 1", "lid": 50},
        ]
        bookings = mock_request.return_value

        # First call: cache miss, fetches from API
        mock_cache.get.return_value = None
        result1 = self.service.get_bookings("user@uchicago.edu")

        # Second call: cache hit
        mock_cache.get.return_value = bookings
        result2 = self.service.get_bookings("user@uchicago.edu")

        self.assertEqual(len(result1), 1)
        self.assertEqual(result1, result2)
        mock_request.assert_called_once()
        mock_cache.set.assert_called_once()

    @patch.object(LibCalService, "_request")
    def test_returns_empty_for_non_list_response(self, mock_request):
        mock_request.return_value = {"error": "something unexpected"}

        with self.assertLogs("mylib_dashboard.services.libcal", level="WARNING"):
            result = self.service.get_bookings("user@uchicago.edu")

        self.assertEqual(result, [])


@override_settings(**LIBCAL_SETTINGS)
class TestGetRoomReservations(TestCase):
    """Tests for LibCalService.get_room_reservations."""

    @classmethod
    def setUpTestData(cls):
        cls.service = LibCalService()

    def setUp(self):
        cache.clear()

    @patch.object(LibCalService, "get_bookings")
    def test_filters_out_sc_locations(self, mock_get_bookings):
        mock_get_bookings.return_value = [
            {"id": 1, "item_name": "Study Room", "lid": 50},
            {"id": 2, "item_name": "SC Reading Room", "lid": 100},  # SC location
        ]

        result = self.service.get_room_reservations("user@uchicago.edu")

        self.assertEqual(len(result["reservations"]), 1)
        self.assertEqual(result["reservations"][0]["roomName"], "Study Room")

    @patch.object(LibCalService, "get_bookings")
    def test_sorts_by_start_time(self, mock_get_bookings):
        mock_get_bookings.return_value = [
            {
                "id": 2,
                "item_name": "Later Room",
                "lid": 50,
                "fromDate": "2026-03-16T14:00:00",
            },
            {
                "id": 1,
                "item_name": "Earlier Room",
                "lid": 50,
                "fromDate": "2026-03-16T10:00:00",
            },
        ]

        result = self.service.get_room_reservations("user@uchicago.edu")

        self.assertEqual(result["reservations"][0]["roomName"], "Earlier Room")
        self.assertEqual(result["reservations"][1]["roomName"], "Later Room")

    @patch.object(LibCalService, "get_bookings")
    def test_empty_bookings(self, mock_get_bookings):
        mock_get_bookings.return_value = []

        result = self.service.get_room_reservations("user@uchicago.edu")

        self.assertEqual(result["reservations"], [])
        self.assertEqual(result["totalReservations"], 0)


@override_settings(**LIBCAL_SETTINGS)
class TestGetSpecialCollectionsSeats(TestCase):
    """Tests for LibCalService.get_special_collections_seats."""

    @classmethod
    def setUpTestData(cls):
        cls.service = LibCalService()

    def setUp(self):
        cache.clear()

    @patch.object(LibCalService, "get_bookings")
    def test_filters_for_sc_locations_only(self, mock_get_bookings):
        mock_get_bookings.return_value = [
            {"id": 1, "item_name": "Study Room", "lid": 50},
            {"id": 2, "item_name": "SC Reading Room", "lid": 100},
        ]

        result = self.service.get_special_collections_seats("user@uchicago.edu")

        self.assertEqual(len(result["reservations"]), 1)
        self.assertEqual(result["reservations"][0]["roomName"], "SC Reading Room")

    @patch.object(LibCalService, "get_bookings")
    def test_empty_when_no_sc_bookings(self, mock_get_bookings):
        mock_get_bookings.return_value = [
            {"id": 1, "item_name": "Study Room", "lid": 50},
        ]

        result = self.service.get_special_collections_seats("user@uchicago.edu")

        self.assertEqual(result["reservations"], [])
        self.assertEqual(result["totalReservations"], 0)


class TestGetLibcalServiceLruCache(TestCase):
    """Tests for get_libcal_service LRU cache."""

    def tearDown(self):
        get_libcal_service.cache_clear()

    @override_settings(**LIBCAL_SETTINGS)
    def test_returns_same_instance(self):
        service1 = get_libcal_service()
        service2 = get_libcal_service()
        self.assertIs(service1, service2)
