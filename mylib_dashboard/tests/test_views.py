"""Tests for mylib_dashboard.views."""

import json
from unittest.mock import patch

from django.test import RequestFactory, TestCase, override_settings

from mylib_dashboard.services.aeon import AeonError
from mylib_dashboard.services.folio import (
    FOLIOError,
    FOLIOUserNotFoundError,
    get_folio_service,
)
from mylib_dashboard.services.illiad import ILLiadError, get_illiad_service
from mylib_dashboard.services.libcal import LibCalError, get_libcal_service
from mylib_dashboard.views import (
    account_blocks,
    downloads,
    fines,
    holds,
    ill_in_process,
    loans,
    paging_requests,
    profile,
    reservations,
    sc_materials,
    sc_seats,
    scan_deliver_in_process,
)

# Minimal settings to avoid import errors when constructing service instances
VIEW_SETTINGS = {
    "DEBUG": False,
    "FOLIO_BASE_URL": "http://folio.test",
    "FOLIO_TENANT": "test",
    "ILLIAD_API_URL": "http://illiad.test",
    "ILLIAD_API_KEY": "testkey",
    "LIBCAL_API_BASE_URL": "http://libcal.test",
    "LIBCAL_CLIENT_ID": "id",
    "LIBCAL_CLIENT_SECRET": "secret",
    "AEON_API_BASE_URL": "http://aeon.test",
    "AEON_API_KEY": "aeonkey",
}


def _make_request(factory, uid=None, email=None):
    """Helper to create a GET request with optional uid and email in META."""
    request = factory.get("/api/test")
    if uid:
        request.META["uid"] = uid
    if email:
        request.META["mail"] = email
    return request


@override_settings(**VIEW_SETTINGS)
class TestRequireCnetidDecorator(TestCase):
    """Tests for the require_cnetid decorator."""

    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()

    def test_returns_401_without_cnetid(self):
        request = _make_request(self.factory)
        response = profile(request)
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.content)
        self.assertIn("Authentication required", data["error"])

    def test_passes_through_with_cnetid(self):
        request = _make_request(self.factory, uid="testuser")
        with patch("mylib_dashboard.views.get_folio_service") as mock_svc:
            mock_svc.return_value.get_user_profile.return_value = {"name": "Test"}
            response = profile(request)
        self.assertEqual(response.status_code, 200)


@override_settings(**VIEW_SETTINGS)
class TestRequireEmailDecorator(TestCase):
    """Tests for the require_email decorator."""

    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()

    def test_returns_400_without_email(self):
        # reservations uses @require_email without @require_cnetid
        request = _make_request(self.factory)
        with self.assertLogs("mylib_dashboard.views", level="WARNING"):
            response = reservations(request)
        self.assertEqual(response.status_code, 400)

    def test_passes_through_with_email(self):
        request = _make_request(self.factory, email="user@uchicago.edu")
        with patch("mylib_dashboard.views.get_libcal_service") as mock_svc:
            mock_svc.return_value.get_room_reservations.return_value = {
                "reservations": [],
                "totalReservations": 0,
            }
            response = reservations(request)
        self.assertEqual(response.status_code, 200)


@override_settings(**VIEW_SETTINGS)
class TestProfileView(TestCase):
    """Tests for the profile view."""

    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()

    def setUp(self):
        get_folio_service.cache_clear()

    @patch("mylib_dashboard.views.get_folio_service")
    def test_success(self, mock_get_svc):
        mock_get_svc.return_value.get_user_profile.return_value = {
            "cnetid": "testuser",
            "displayName": "Test User",
        }
        request = _make_request(self.factory, uid="testuser")

        response = profile(request)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["displayName"], "Test User")

    @patch("mylib_dashboard.views.get_folio_service")
    def test_user_not_found(self, mock_get_svc):
        mock_get_svc.return_value.get_user_profile.side_effect = FOLIOUserNotFoundError(
            "Not found"
        )
        request = _make_request(self.factory, uid="unknown")

        with self.assertLogs("mylib_dashboard.views", level="WARNING"):
            response = profile(request)

        self.assertEqual(response.status_code, 404)

    @patch("mylib_dashboard.views.get_folio_service")
    def test_service_error(self, mock_get_svc):
        mock_get_svc.return_value.get_user_profile.side_effect = FOLIOError("API down")
        request = _make_request(self.factory, uid="testuser")

        with self.assertLogs("mylib_dashboard.views", level="ERROR"):
            response = profile(request)

        self.assertEqual(response.status_code, 503)


@override_settings(**VIEW_SETTINGS)
class TestLoansView(TestCase):
    """Tests for the loans view."""

    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()

    def setUp(self):
        get_folio_service.cache_clear()

    @patch("mylib_dashboard.views.get_folio_service")
    def test_success(self, mock_get_svc):
        mock_get_svc.return_value.get_user_loans_categorized.return_value = {
            "standardLoans": [],
            "shortTermLoans": [],
            "totalLoans": 0,
        }
        request = _make_request(self.factory, uid="testuser")

        response = loans(request)

        self.assertEqual(response.status_code, 200)

    @patch("mylib_dashboard.views.get_folio_service")
    def test_user_not_found(self, mock_get_svc):
        mock_get_svc.return_value.get_user_loans_categorized.side_effect = (
            FOLIOUserNotFoundError("Not found")
        )
        request = _make_request(self.factory, uid="unknown")

        with self.assertLogs("mylib_dashboard.views", level="WARNING"):
            response = loans(request)
        self.assertEqual(response.status_code, 404)

    @patch("mylib_dashboard.views.get_folio_service")
    def test_service_error(self, mock_get_svc):
        mock_get_svc.return_value.get_user_loans_categorized.side_effect = FOLIOError(
            "fail"
        )
        request = _make_request(self.factory, uid="testuser")

        with self.assertLogs("mylib_dashboard.views", level="ERROR"):
            response = loans(request)
        self.assertEqual(response.status_code, 503)


@override_settings(**VIEW_SETTINGS)
class TestHoldsView(TestCase):
    """Tests for the holds view."""

    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()

    def setUp(self):
        get_folio_service.cache_clear()

    @patch("mylib_dashboard.views.get_folio_service")
    def test_success(self, mock_get_svc):
        mock_get_svc.return_value.get_user_holds.return_value = {
            "holds": [],
            "totalHolds": 0,
        }
        request = _make_request(self.factory, uid="testuser")

        response = holds(request)
        self.assertEqual(response.status_code, 200)

    @patch("mylib_dashboard.views.get_folio_service")
    def test_user_not_found(self, mock_get_svc):
        mock_get_svc.return_value.get_user_holds.side_effect = FOLIOUserNotFoundError(
            "Not found"
        )
        request = _make_request(self.factory, uid="unknown")

        with self.assertLogs("mylib_dashboard.views", level="WARNING"):
            response = holds(request)
        self.assertEqual(response.status_code, 404)

    @patch("mylib_dashboard.views.get_folio_service")
    def test_service_error(self, mock_get_svc):
        mock_get_svc.return_value.get_user_holds.side_effect = FOLIOError("fail")
        request = _make_request(self.factory, uid="testuser")

        with self.assertLogs("mylib_dashboard.views", level="ERROR"):
            response = holds(request)
        self.assertEqual(response.status_code, 503)


@override_settings(**VIEW_SETTINGS)
class TestFinesView(TestCase):
    """Tests for the fines view."""

    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()

    def setUp(self):
        get_folio_service.cache_clear()

    @patch("mylib_dashboard.views.get_folio_service")
    def test_success(self, mock_get_svc):
        mock_get_svc.return_value.get_user_fines.return_value = {
            "fines": [],
            "totalAmount": 0.0,
            "totalFines": 0,
        }
        request = _make_request(self.factory, uid="testuser")

        response = fines(request)
        self.assertEqual(response.status_code, 200)

    @patch("mylib_dashboard.views.get_folio_service")
    def test_user_not_found(self, mock_get_svc):
        mock_get_svc.return_value.get_user_fines.side_effect = FOLIOUserNotFoundError(
            "Not found"
        )
        request = _make_request(self.factory, uid="unknown")

        with self.assertLogs("mylib_dashboard.views", level="WARNING"):
            response = fines(request)
        self.assertEqual(response.status_code, 404)

    @patch("mylib_dashboard.views.get_folio_service")
    def test_service_error(self, mock_get_svc):
        mock_get_svc.return_value.get_user_fines.side_effect = FOLIOError("fail")
        request = _make_request(self.factory, uid="testuser")

        with self.assertLogs("mylib_dashboard.views", level="ERROR"):
            response = fines(request)
        self.assertEqual(response.status_code, 503)


@override_settings(**VIEW_SETTINGS)
class TestAccountBlocksView(TestCase):
    """Tests for the account_blocks view."""

    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()

    def setUp(self):
        get_folio_service.cache_clear()

    @patch("mylib_dashboard.views.get_folio_service")
    def test_success(self, mock_get_svc):
        mock_get_svc.return_value.get_user_blocks.return_value = {
            "blocks": [],
            "hasBlocks": False,
        }
        request = _make_request(self.factory, uid="testuser")

        response = account_blocks(request)
        self.assertEqual(response.status_code, 200)

    @patch("mylib_dashboard.views.get_folio_service")
    def test_user_not_found(self, mock_get_svc):
        mock_get_svc.return_value.get_user_blocks.side_effect = FOLIOUserNotFoundError(
            "Not found"
        )
        request = _make_request(self.factory, uid="unknown")

        with self.assertLogs("mylib_dashboard.views", level="WARNING"):
            response = account_blocks(request)
        self.assertEqual(response.status_code, 404)

    @patch("mylib_dashboard.views.get_folio_service")
    def test_service_error(self, mock_get_svc):
        mock_get_svc.return_value.get_user_blocks.side_effect = FOLIOError("fail")
        request = _make_request(self.factory, uid="testuser")

        with self.assertLogs("mylib_dashboard.views", level="ERROR"):
            response = account_blocks(request)
        self.assertEqual(response.status_code, 503)


@override_settings(**VIEW_SETTINGS)
class TestDownloadsView(TestCase):
    """Tests for the downloads view."""

    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()

    def setUp(self):
        get_illiad_service.cache_clear()

    @patch("mylib_dashboard.views.get_illiad_service")
    def test_success(self, mock_get_svc):
        mock_get_svc.return_value.get_copies_ready.return_value = {
            "copies": [],
            "totalCopies": 0,
        }
        request = _make_request(self.factory, uid="testuser", email="user@uchicago.edu")

        response = downloads(request)
        self.assertEqual(response.status_code, 200)

    @patch("mylib_dashboard.views.get_illiad_service")
    def test_requires_email(self, mock_get_svc):
        # Has cnetid but no email
        request = _make_request(self.factory, uid="testuser")

        with self.assertLogs("mylib_dashboard.views", level="WARNING"):
            response = downloads(request)
        self.assertEqual(response.status_code, 400)

    @patch("mylib_dashboard.views.get_illiad_service")
    def test_service_error(self, mock_get_svc):
        mock_get_svc.return_value.get_copies_ready.side_effect = ILLiadError("fail")
        request = _make_request(self.factory, uid="testuser", email="user@uchicago.edu")

        with self.assertLogs("mylib_dashboard.views", level="ERROR"):
            response = downloads(request)
        self.assertEqual(response.status_code, 503)


@override_settings(**VIEW_SETTINGS)
class TestIllInProcessView(TestCase):
    """Tests for the ill_in_process view."""

    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()

    def setUp(self):
        get_illiad_service.cache_clear()

    @patch("mylib_dashboard.views.get_illiad_service")
    def test_success(self, mock_get_svc):
        mock_get_svc.return_value.get_ill_in_process.return_value = {
            "requests": [],
            "totalRequests": 0,
        }
        request = _make_request(self.factory, uid="testuser", email="user@uchicago.edu")

        response = ill_in_process(request)
        self.assertEqual(response.status_code, 200)

    @patch("mylib_dashboard.views.get_illiad_service")
    def test_requires_email(self, mock_get_svc):
        request = _make_request(self.factory, uid="testuser")

        with self.assertLogs("mylib_dashboard.views", level="WARNING"):
            response = ill_in_process(request)
        self.assertEqual(response.status_code, 400)

    @patch("mylib_dashboard.views.get_illiad_service")
    def test_service_error(self, mock_get_svc):
        mock_get_svc.return_value.get_ill_in_process.side_effect = ILLiadError("fail")
        request = _make_request(self.factory, uid="testuser", email="user@uchicago.edu")

        with self.assertLogs("mylib_dashboard.views", level="ERROR"):
            response = ill_in_process(request)
        self.assertEqual(response.status_code, 503)


@override_settings(**VIEW_SETTINGS)
class TestScanDeliverInProcessView(TestCase):
    """Tests for the scan_deliver_in_process view."""

    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()

    def setUp(self):
        get_illiad_service.cache_clear()

    @patch("mylib_dashboard.views.get_illiad_service")
    def test_success(self, mock_get_svc):
        mock_get_svc.return_value.get_scan_deliver_in_process.return_value = {
            "requests": [],
            "totalRequests": 0,
        }
        request = _make_request(self.factory, uid="testuser", email="user@uchicago.edu")

        response = scan_deliver_in_process(request)
        self.assertEqual(response.status_code, 200)

    @patch("mylib_dashboard.views.get_illiad_service")
    def test_requires_email(self, mock_get_svc):
        request = _make_request(self.factory, uid="testuser")

        with self.assertLogs("mylib_dashboard.views", level="WARNING"):
            response = scan_deliver_in_process(request)
        self.assertEqual(response.status_code, 400)

    @patch("mylib_dashboard.views.get_illiad_service")
    def test_service_error(self, mock_get_svc):
        mock_get_svc.return_value.get_scan_deliver_in_process.side_effect = ILLiadError(
            "fail"
        )
        request = _make_request(self.factory, uid="testuser", email="user@uchicago.edu")

        with self.assertLogs("mylib_dashboard.views", level="ERROR"):
            response = scan_deliver_in_process(request)
        self.assertEqual(response.status_code, 503)


@override_settings(**VIEW_SETTINGS)
class TestReservationsView(TestCase):
    """Tests for the reservations view."""

    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()

    def setUp(self):
        get_libcal_service.cache_clear()

    @patch("mylib_dashboard.views.get_libcal_service")
    def test_success(self, mock_get_svc):
        mock_get_svc.return_value.get_room_reservations.return_value = {
            "reservations": [{"id": "1", "roomName": "Room 201"}],
            "totalReservations": 1,
        }
        request = _make_request(self.factory, email="user@uchicago.edu")

        response = reservations(request)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["totalReservations"], 1)

    def test_requires_email(self):
        request = _make_request(self.factory)

        with self.assertLogs("mylib_dashboard.views", level="WARNING"):
            response = reservations(request)
        self.assertEqual(response.status_code, 400)

    @patch("mylib_dashboard.views.get_libcal_service")
    def test_service_error(self, mock_get_svc):
        mock_get_svc.return_value.get_room_reservations.side_effect = LibCalError(
            "fail"
        )
        request = _make_request(self.factory, email="user@uchicago.edu")

        with self.assertLogs("mylib_dashboard.views", level="ERROR"):
            response = reservations(request)
        self.assertEqual(response.status_code, 503)


@override_settings(**VIEW_SETTINGS)
class TestScSeatsView(TestCase):
    """Tests for the sc_seats view."""

    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()

    def setUp(self):
        get_libcal_service.cache_clear()

    @patch("mylib_dashboard.views.get_libcal_service")
    def test_success(self, mock_get_svc):
        mock_get_svc.return_value.get_special_collections_seats.return_value = {
            "reservations": [],
            "totalReservations": 0,
        }
        request = _make_request(self.factory, email="user@uchicago.edu")

        response = sc_seats(request)
        self.assertEqual(response.status_code, 200)

    @patch("mylib_dashboard.views.get_libcal_service")
    def test_service_error(self, mock_get_svc):
        mock_get_svc.return_value.get_special_collections_seats.side_effect = (
            LibCalError("fail")
        )
        request = _make_request(self.factory, email="user@uchicago.edu")

        with self.assertLogs("mylib_dashboard.views", level="ERROR"):
            response = sc_seats(request)
        self.assertEqual(response.status_code, 503)


@override_settings(**VIEW_SETTINGS)
class TestPagingRequestsView(TestCase):
    """Tests for the paging_requests view."""

    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()

    def setUp(self):
        get_folio_service.cache_clear()

    @patch("mylib_dashboard.views.get_folio_service")
    def test_success(self, mock_get_svc):
        mock_get_svc.return_value.get_paging_requests.return_value = {
            "requests": [],
            "totalRequests": 0,
        }
        request = _make_request(self.factory, uid="testuser")

        response = paging_requests(request)
        self.assertEqual(response.status_code, 200)

    @patch("mylib_dashboard.views.get_folio_service")
    def test_user_not_found(self, mock_get_svc):
        mock_get_svc.return_value.get_paging_requests.side_effect = (
            FOLIOUserNotFoundError("Not found")
        )
        request = _make_request(self.factory, uid="unknown")

        with self.assertLogs("mylib_dashboard.views", level="WARNING"):
            response = paging_requests(request)
        self.assertEqual(response.status_code, 404)

    @patch("mylib_dashboard.views.get_folio_service")
    def test_service_error(self, mock_get_svc):
        mock_get_svc.return_value.get_paging_requests.side_effect = FOLIOError("fail")
        request = _make_request(self.factory, uid="testuser")

        with self.assertLogs("mylib_dashboard.views", level="ERROR"):
            response = paging_requests(request)
        self.assertEqual(response.status_code, 503)


@override_settings(**VIEW_SETTINGS)
class TestScMaterialsView(TestCase):
    """Tests for the sc_materials view."""

    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()

    @patch("mylib_dashboard.views.get_aeon_service")
    def test_success(self, mock_get_svc):
        mock_get_svc.return_value.get_user_requests.return_value = {
            "requests": [],
            "totalRequests": 0,
        }
        request = _make_request(self.factory, email="user@uchicago.edu")

        response = sc_materials(request)
        self.assertEqual(response.status_code, 200)

    @patch("mylib_dashboard.views.get_aeon_service")
    def test_service_error(self, mock_get_svc):
        mock_get_svc.return_value.get_user_requests.side_effect = AeonError("fail")
        request = _make_request(self.factory, email="user@uchicago.edu")

        with self.assertLogs("mylib_dashboard.views", level="ERROR"):
            response = sc_materials(request)
        self.assertEqual(response.status_code, 503)
