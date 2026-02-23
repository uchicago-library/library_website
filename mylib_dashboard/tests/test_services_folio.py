"""Tests for mylib_dashboard.services.folio."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import requests as real_requests
from django.core.cache import cache
from django.test import TestCase, override_settings

from item_servlet.utils import FOLIOAuthError
from mylib_dashboard.services.folio import (
    FOLIOError,
    FOLIOService,
    FOLIOUserNotFoundError,
    get_folio_service,
)

FOLIO_SETTINGS = {
    "FOLIO_BASE_URL": "http://folio.test",
    "FOLIO_TENANT": "test_tenant",
    "FOLIO_TIMEOUT": 10,
    "FOLIO_PROXY": None,
}


@override_settings(**FOLIO_SETTINGS)
class TestFOLIOServiceInit(TestCase):
    """Tests for FOLIOService.__init__."""

    def test_reads_settings(self):
        service = FOLIOService()
        self.assertEqual(service.base_url, "http://folio.test")
        self.assertEqual(service.tenant, "test_tenant")
        self.assertEqual(service.timeout, 10)
        self.assertIsNone(service.proxies)

    @override_settings(FOLIO_PROXY="socks5://localhost:1080")
    def test_configures_proxy_when_set(self):
        service = FOLIOService()
        self.assertEqual(
            service.proxies,
            {
                "http": "socks5://localhost:1080",
                "https": "socks5://localhost:1080",
            },
        )


@override_settings(**FOLIO_SETTINGS)
class TestFOLIOServiceGetToken(TestCase):
    """Tests for FOLIOService._get_token."""

    @classmethod
    def setUpTestData(cls):
        cls.service = FOLIOService()

    @patch("mylib_dashboard.services.folio.get_auth")
    def test_returns_token_from_get_auth(self, mock_get_auth):
        mock_get_auth.return_value = {"x-okapi-token": "test-token-123"}
        token = self.service._get_token()
        self.assertEqual(token, "test-token-123")
        mock_get_auth.assert_called_once()

    @patch("mylib_dashboard.services.folio.get_auth")
    def test_raises_folio_error_on_auth_failure(self, mock_get_auth):
        mock_get_auth.side_effect = FOLIOAuthError("Auth failed")
        with self.assertRaises(FOLIOError) as ctx:
            self.service._get_token()
        self.assertIn("Auth failed", str(ctx.exception))


@override_settings(**FOLIO_SETTINGS)
class TestFOLIOServiceRequest(TestCase):
    """Tests for FOLIOService._request."""

    @classmethod
    def setUpTestData(cls):
        cls.service = FOLIOService()

    @patch("mylib_dashboard.services.folio.requests")
    @patch("mylib_dashboard.services.folio.get_auth")
    def test_successful_request(self, mock_get_auth, mock_requests):
        mock_get_auth.return_value = {"x-okapi-token": "tok"}
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": "value"}
        mock_requests.request.return_value = mock_response

        result = self.service._request("GET", "/test-endpoint")

        self.assertEqual(result, {"data": "value"})
        mock_requests.request.assert_called_once()
        call_kwargs = mock_requests.request.call_args
        self.assertEqual(call_kwargs[0][0], "GET")
        self.assertIn("http://folio.test/test-endpoint", call_kwargs[0][1])

    @patch("mylib_dashboard.services.folio.requests")
    @patch("mylib_dashboard.services.folio.get_auth")
    def test_timeout_raises_folio_error(self, mock_get_auth, mock_requests):

        mock_get_auth.return_value = {"x-okapi-token": "tok"}
        mock_requests.request.side_effect = real_requests.exceptions.Timeout()
        mock_requests.exceptions = real_requests.exceptions

        with self.assertLogs("mylib_dashboard.services.folio", level="ERROR"):
            with self.assertRaises(FOLIOError) as ctx:
                self.service._request("GET", "/test")
        self.assertIn("timed out", str(ctx.exception))

    @patch("mylib_dashboard.services.folio.requests")
    @patch("mylib_dashboard.services.folio.get_auth")
    def test_http_error_raises_folio_error(self, mock_get_auth, mock_requests):

        mock_get_auth.return_value = {"x-okapi-token": "tok"}
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        error = real_requests.exceptions.HTTPError(response=mock_resp)
        mock_requests.request.side_effect = error
        mock_requests.exceptions = real_requests.exceptions

        with self.assertLogs("mylib_dashboard.services.folio", level="ERROR"):
            with self.assertRaises(FOLIOError) as ctx:
                self.service._request("GET", "/test")
        self.assertIn("500", str(ctx.exception))

    @patch("mylib_dashboard.services.folio.requests")
    @patch("mylib_dashboard.services.folio.get_auth")
    def test_request_exception_raises_folio_error(self, mock_get_auth, mock_requests):

        mock_get_auth.return_value = {"x-okapi-token": "tok"}
        mock_requests.request.side_effect = real_requests.exceptions.ConnectionError(
            "Connection refused"
        )
        mock_requests.exceptions = real_requests.exceptions

        with self.assertLogs("mylib_dashboard.services.folio", level="ERROR"):
            with self.assertRaises(FOLIOError):
                self.service._request("GET", "/test")


@override_settings(**FOLIO_SETTINGS)
class TestGetUserByCnetid(TestCase):
    """Tests for FOLIOService.get_user_by_cnetid."""

    @classmethod
    def setUpTestData(cls):
        cls.service = FOLIOService()
        cls.sample_folio_user = {
            "id": "user-uuid-123",
            "username": "testuser",
            "active": True,
            "expirationDate": "2027-01-01",
            "patronGroup": "pg-123",
            "personal": {
                "firstName": "John",
                "lastName": "Doe",
                "email": "jdoe@uchicago.edu",
            },
            "customFields": {
                "staffDepartment": "Library IT",
            },
        }

    def setUp(self):
        cache.clear()

    @patch.object(FOLIOService, "_request")
    def test_returns_user_data(self, mock_request):
        mock_request.return_value = {"users": [self.sample_folio_user]}

        result = self.service.get_user_by_cnetid("testuser")

        self.assertEqual(result["id"], "user-uuid-123")
        self.assertEqual(result["firstName"], "John")
        self.assertEqual(result["lastName"], "Doe")
        self.assertEqual(result["email"], "jdoe@uchicago.edu")
        self.assertEqual(result["department"], "Library IT")
        self.assertTrue(result["active"])

    @patch.object(FOLIOService, "_request")
    def test_uses_preferred_first_name(self, mock_request):
        user = {
            **self.sample_folio_user,
            "personal": {
                **self.sample_folio_user["personal"],
                "preferredFirstName": "Johnny",
            },
        }
        mock_request.return_value = {"users": [user]}

        result = self.service.get_user_by_cnetid("testuser")
        self.assertEqual(result["firstName"], "Johnny")

    @patch.object(FOLIOService, "_request")
    def test_extracts_staff_department(self, mock_request):
        mock_request.return_value = {"users": [self.sample_folio_user]}
        result = self.service.get_user_by_cnetid("testuser")
        self.assertEqual(result["department"], "Library IT")

    @patch("mylib_dashboard.services.folio.cache")
    @patch.object(FOLIOService, "_request")
    def test_caches_result(self, mock_request, mock_cache):
        mock_request.return_value = {"users": [self.sample_folio_user]}
        expected = {
            "id": "user-uuid-123",
            "firstName": "John",
            "lastName": "Doe",
            "email": "jdoe@uchicago.edu",
            "department": "Library IT",
            "active": True,
            "expirationDate": "2027-01-01",
            "patronGroup": "pg-123",
        }

        # First call: cache miss, fetches from API
        mock_cache.get.return_value = None
        result1 = self.service.get_user_by_cnetid("testuser")

        # Second call: cache hit
        mock_cache.get.return_value = expected
        result2 = self.service.get_user_by_cnetid("testuser")

        self.assertEqual(result1, result2)
        mock_request.assert_called_once()
        mock_cache.set.assert_called_once()

    @patch.object(FOLIOService, "_request")
    def test_user_not_found_raises_error(self, mock_request):
        mock_request.return_value = {"users": []}

        with self.assertLogs("mylib_dashboard.services.folio", level="WARNING"):
            with self.assertRaises(FOLIOUserNotFoundError):
                self.service.get_user_by_cnetid("nonexistent")


@override_settings(**FOLIO_SETTINGS)
class TestGetUserProfile(TestCase):
    """Tests for FOLIOService.get_user_profile."""

    @classmethod
    def setUpTestData(cls):
        cls.service = FOLIOService()

    def setUp(self):
        cache.clear()

    @patch.object(FOLIOService, "get_user_by_cnetid")
    def test_returns_formatted_profile(self, mock_get_user):
        mock_get_user.return_value = {
            "id": "uuid-1",
            "firstName": "Jane",
            "lastName": "Smith",
            "email": "jsmith@uchicago.edu",
            "department": "Chemistry",
            "active": True,
            "expirationDate": "2027-06-01",
        }

        result = self.service.get_user_profile("jsmith")

        # cnetid comes from the auth layer, not the FOLIO response
        self.assertEqual(result["cnetid"], "jsmith")
        self.assertEqual(result["uuid"], "uuid-1")
        self.assertEqual(result["displayName"], "Jane Smith")
        self.assertEqual(result["department"], "Chemistry")

    @patch.object(FOLIOService, "get_user_by_cnetid")
    def test_display_name_with_empty_last_name(self, mock_get_user):
        mock_get_user.return_value = {
            "id": "uuid-2",
            "firstName": "Bob",
            "lastName": "",
            "email": "bob@uchicago.edu",
            "department": "",
            "active": True,
            "expirationDate": None,
        }

        result = self.service.get_user_profile("bob")
        self.assertEqual(result["displayName"], "Bob")

    @patch.object(FOLIOService, "get_user_by_cnetid")
    def test_display_name_with_empty_first_name(self, mock_get_user):
        mock_get_user.return_value = {
            "id": "uuid-3",
            "firstName": "",
            "lastName": "Smith",
            "email": "smith@uchicago.edu",
            "department": "",
            "active": True,
            "expirationDate": None,
        }

        result = self.service.get_user_profile("smith")
        self.assertEqual(result["displayName"], "Smith")

    @patch.object(FOLIOService, "get_user_by_cnetid")
    def test_display_name_with_both_names_empty(self, mock_get_user):
        mock_get_user.return_value = {
            "id": "uuid-4",
            "firstName": "",
            "lastName": "",
            "email": "unknown@uchicago.edu",
            "department": "",
            "active": True,
            "expirationDate": None,
        }

        result = self.service.get_user_profile("unknown")
        self.assertEqual(result["displayName"], "")


@override_settings(**FOLIO_SETTINGS)
class TestParseDueDate(TestCase):
    """Tests for FOLIOService._parse_due_date."""

    @classmethod
    def setUpTestData(cls):
        cls.service = FOLIOService()

    def test_parses_iso_date(self):
        result = self.service._parse_due_date("2026-03-15T10:00:00Z")
        self.assertEqual(result.year, 2026)
        self.assertEqual(result.month, 3)
        self.assertEqual(result.day, 15)

    def test_returns_none_for_empty(self):
        self.assertIsNone(self.service._parse_due_date(""))
        self.assertIsNone(self.service._parse_due_date(None))

    def test_returns_none_for_invalid(self):
        with self.assertLogs("mylib_dashboard.services.folio", level="WARNING"):
            self.assertIsNone(self.service._parse_due_date("not-a-date"))


@override_settings(**FOLIO_SETTINGS)
class TestComputeLoanStatus(TestCase):
    """Tests for FOLIOService._compute_loan_status."""

    @classmethod
    def setUpTestData(cls):
        cls.service = FOLIOService()

    @patch("mylib_dashboard.services.folio.datetime")
    def test_overdue_loan(self, mock_datetime):
        mock_datetime.now.return_value = datetime(
            2026, 3, 15, 12, 0, tzinfo=timezone.utc
        )
        mock_datetime.fromisoformat = datetime.fromisoformat
        mock_datetime.side_effect = lambda *a, **kw: datetime(*a, **kw)

        loan = {"dueDate": "2026-03-14T10:00:00+00:00"}
        status = self.service._compute_loan_status(loan)

        self.assertTrue(status["isOverdue"])
        self.assertFalse(status["isDueSoon"])

    @patch("mylib_dashboard.services.folio.datetime")
    def test_due_soon_loan(self, mock_datetime):
        mock_datetime.now.return_value = datetime(
            2026, 3, 15, 12, 0, tzinfo=timezone.utc
        )
        mock_datetime.fromisoformat = datetime.fromisoformat
        mock_datetime.side_effect = lambda *a, **kw: datetime(*a, **kw)

        # Due in 12 hours (within 24h threshold)
        loan = {"dueDate": "2026-03-16T00:00:00+00:00"}
        status = self.service._compute_loan_status(loan)

        self.assertFalse(status["isOverdue"])
        self.assertTrue(status["isDueSoon"])

    @patch("mylib_dashboard.services.folio.datetime")
    def test_normal_loan(self, mock_datetime):
        mock_datetime.now.return_value = datetime(
            2026, 3, 15, 12, 0, tzinfo=timezone.utc
        )
        mock_datetime.fromisoformat = datetime.fromisoformat
        mock_datetime.side_effect = lambda *a, **kw: datetime(*a, **kw)

        # Due in 3 days (well beyond 24h threshold)
        loan = {"dueDate": "2026-03-18T12:00:00+00:00"}
        status = self.service._compute_loan_status(loan)

        self.assertFalse(status["isOverdue"])
        self.assertFalse(status["isDueSoon"])
        self.assertFalse(status["isRecalled"])

    def test_recalled_loan(self):
        loan = {
            "dueDate": "2026-06-01T10:00:00+00:00",
            "action": "recallrequested",
        }
        status = self.service._compute_loan_status(loan)
        self.assertTrue(status["isRecalled"])

    def test_no_due_date(self):
        loan = {}
        status = self.service._compute_loan_status(loan)
        self.assertFalse(status["isOverdue"])
        self.assertFalse(status["isDueSoon"])
        self.assertFalse(status["isRecalled"])


@override_settings(**FOLIO_SETTINGS)
class TestFormatLoan(TestCase):
    """Tests for FOLIOService._format_loan."""

    @classmethod
    def setUpTestData(cls):
        cls.service = FOLIOService()

    def test_formats_loan_with_all_fields(self):
        loan = {
            "id": "loan-1",
            "itemId": "item-1",
            "item": {
                "title": "Test Book",
                "contributors": [{"name": "Author One"}],
                "barcode": "12345",
            },
            "dueDate": "2026-04-01T10:00:00Z",
            "renewalCount": 2,
            "loanPolicyId": "policy-1",
        }
        status = {"isOverdue": False, "isDueSoon": False, "isRecalled": False}

        result = self.service._format_loan(loan, status)

        self.assertEqual(result["id"], "loan-1")
        self.assertEqual(result["title"], "Test Book")
        self.assertEqual(result["author"], "Author One")
        self.assertEqual(result["barcode"], "12345")
        self.assertEqual(result["renewalCount"], 2)
        self.assertFalse(result["isOverdue"])

    def test_handles_missing_contributors(self):
        loan = {
            "id": "loan-2",
            "item": {"title": "No Author Book", "contributors": []},
        }
        status = {"isOverdue": False, "isDueSoon": False, "isRecalled": False}

        result = self.service._format_loan(loan, status)
        self.assertEqual(result["author"], "")

    def test_handles_missing_item(self):
        loan = {"id": "loan-3"}
        status = {"isOverdue": False, "isDueSoon": False, "isRecalled": False}

        result = self.service._format_loan(loan, status)
        self.assertEqual(result["title"], "Unknown Title")
        self.assertEqual(result["author"], "")


@override_settings(
    **FOLIO_SETTINGS,
    FOLIO_SHORT_TERM_LOAN_POLICY_IDS=["short-policy-1"],
)
class TestGetUserLoansCategorized(TestCase):
    """Tests for FOLIOService.get_user_loans_categorized."""

    @classmethod
    def setUpTestData(cls):
        cls.service = FOLIOService()

    def setUp(self):
        cache.clear()

    @patch.object(FOLIOService, "get_user_loans")
    @patch.object(FOLIOService, "get_user_by_cnetid")
    def test_categorizes_standard_and_short_term(self, mock_get_user, mock_get_loans):
        mock_get_user.return_value = {"id": "uuid-1"}
        mock_get_loans.return_value = [
            {
                "id": "loan-1",
                "loanPolicyId": "standard-policy",
                "dueDate": "2026-06-01T10:00:00+00:00",
                "item": {"title": "Standard Book"},
            },
            {
                "id": "loan-2",
                "loanPolicyId": "short-policy-1",
                "dueDate": "2026-03-20T10:00:00+00:00",
                "item": {"title": "Short Term Book"},
            },
        ]

        result = self.service.get_user_loans_categorized("testuser")

        self.assertEqual(len(result["standardLoans"]), 1)
        self.assertEqual(len(result["shortTermLoans"]), 1)
        self.assertEqual(result["totalLoans"], 2)
        self.assertEqual(result["standardLoans"][0]["title"], "Standard Book")
        self.assertEqual(result["shortTermLoans"][0]["title"], "Short Term Book")

    @patch.object(FOLIOService, "get_user_loans")
    @patch.object(FOLIOService, "get_user_by_cnetid")
    def test_empty_loans(self, mock_get_user, mock_get_loans):
        mock_get_user.return_value = {"id": "uuid-1"}
        mock_get_loans.return_value = []

        result = self.service.get_user_loans_categorized("testuser")

        self.assertEqual(result["standardLoans"], [])
        self.assertEqual(result["shortTermLoans"], [])
        self.assertEqual(result["totalLoans"], 0)

    @patch("mylib_dashboard.services.folio.datetime")
    @patch.object(FOLIOService, "get_user_loans")
    @patch.object(FOLIOService, "get_user_by_cnetid")
    def test_counts_overdue_recalled_due_soon(
        self, mock_get_user, mock_get_loans, mock_datetime
    ):
        mock_datetime.now.return_value = datetime(
            2026, 3, 15, 12, 0, tzinfo=timezone.utc
        )
        mock_datetime.fromisoformat = datetime.fromisoformat
        mock_datetime.side_effect = lambda *a, **kw: datetime(*a, **kw)

        mock_get_user.return_value = {"id": "uuid-1"}
        mock_get_loans.return_value = [
            {
                "id": "loan-overdue",
                "loanPolicyId": "standard",
                "dueDate": "2026-03-10T10:00:00+00:00",
                "item": {"title": "Overdue"},
            },
            {
                "id": "loan-recalled",
                "loanPolicyId": "standard",
                "dueDate": "2026-06-01T10:00:00+00:00",
                "action": "recallrequested",
                "item": {"title": "Recalled"},
            },
            {
                "id": "loan-due-soon",
                "loanPolicyId": "standard",
                "dueDate": "2026-03-16T06:00:00+00:00",
                "item": {"title": "Due Soon"},
            },
        ]

        result = self.service.get_user_loans_categorized("testuser")

        self.assertEqual(result["overdueCount"], 1)
        self.assertEqual(result["recalledCount"], 1)
        self.assertEqual(result["dueSoonCount"], 1)

    @patch.object(FOLIOService, "get_user_loans")
    @patch.object(FOLIOService, "get_user_by_cnetid")
    def test_sorts_by_due_date(self, mock_get_user, mock_get_loans):
        mock_get_user.return_value = {"id": "uuid-1"}
        mock_get_loans.return_value = [
            {
                "id": "loan-later",
                "loanPolicyId": "standard",
                "dueDate": "2026-06-01T10:00:00+00:00",
                "item": {"title": "Later"},
            },
            {
                "id": "loan-sooner",
                "loanPolicyId": "standard",
                "dueDate": "2026-04-01T10:00:00+00:00",
                "item": {"title": "Sooner"},
            },
        ]

        result = self.service.get_user_loans_categorized("testuser")

        self.assertEqual(result["standardLoans"][0]["title"], "Sooner")
        self.assertEqual(result["standardLoans"][1]["title"], "Later")


@override_settings(**FOLIO_SETTINGS)
class TestGetServicePoints(TestCase):
    """Tests for FOLIOService.get_service_points."""

    @classmethod
    def setUpTestData(cls):
        cls.service = FOLIOService()

    def setUp(self):
        cache.clear()

    @patch.object(FOLIOService, "_request")
    def test_fetches_service_points(self, mock_request):
        mock_request.return_value = {
            "servicepoints": [
                {
                    "id": "sp-1",
                    "discoveryDisplayName": "Regenstein Circ",
                    "name": "Reg",
                },
                {"id": "sp-2", "name": "Mansueto"},
            ]
        }

        result = self.service.get_service_points()

        self.assertEqual(result["sp-1"], "Regenstein Circ")
        self.assertEqual(result["sp-2"], "Mansueto")

    @patch("mylib_dashboard.services.folio.cache")
    @patch.object(FOLIOService, "_request")
    def test_returns_cached_service_points(self, mock_request, mock_cache):
        mock_request.return_value = {"servicepoints": [{"id": "sp-1", "name": "Test"}]}
        expected = {"sp-1": "Test"}

        # First call: cache miss, fetches from API
        mock_cache.get.return_value = None
        self.service.get_service_points()

        # Second call: cache hit
        mock_cache.get.return_value = expected
        result = self.service.get_service_points()

        self.assertEqual(result, expected)
        mock_request.assert_called_once()
        mock_cache.set.assert_called_once()

    @patch.object(FOLIOService, "_request")
    def test_get_service_points_uses_discovery_display_name(self, mock_request):
        mock_request.return_value = {
            "servicepoints": [
                {
                    "id": "sp-1",
                    "discoveryDisplayName": "Display Name",
                    "name": "Internal",
                },
            ]
        }

        result = self.service.get_service_points()
        self.assertEqual(result["sp-1"], "Display Name")


@override_settings(**FOLIO_SETTINGS)
class TestGetUserHolds(TestCase):
    """Tests for FOLIOService.get_user_holds."""

    @classmethod
    def setUpTestData(cls):
        cls.service = FOLIOService()

    def setUp(self):
        cache.clear()

    @patch.object(FOLIOService, "get_service_points")
    @patch.object(FOLIOService, "_request")
    @patch.object(FOLIOService, "get_user_by_cnetid")
    def test_returns_holds_with_pickup_locations(
        self, mock_get_user, mock_request, mock_sp
    ):
        mock_get_user.return_value = {"id": "uuid-1"}
        mock_sp.return_value = {"sp-1": "Regenstein Circ Desk"}
        mock_request.return_value = {
            "requests": [
                {
                    "id": "req-1",
                    "instance": {"title": "Hold Book"},
                    "requestType": "Hold",
                    "pickupServicePointId": "sp-1",
                    "holdShelfExpirationDate": "2026-04-01",
                    "position": 1,
                },
            ]
        }

        result = self.service.get_user_holds("testuser")

        self.assertEqual(len(result["holds"]), 1)
        self.assertEqual(result["totalHolds"], 1)
        self.assertEqual(result["holds"][0]["title"], "Hold Book")
        self.assertEqual(result["holds"][0]["pickupLocation"], "Regenstein Circ Desk")

    @patch.object(FOLIOService, "get_service_points")
    @patch.object(FOLIOService, "_request")
    @patch.object(FOLIOService, "get_user_by_cnetid")
    def test_empty_holds(self, mock_get_user, mock_request, mock_sp):
        mock_get_user.return_value = {"id": "uuid-1"}
        mock_sp.return_value = {}
        mock_request.return_value = {"requests": []}

        result = self.service.get_user_holds("testuser")

        self.assertEqual(result["holds"], [])
        self.assertEqual(result["totalHolds"], 0)

    @patch.object(FOLIOService, "get_service_points")
    @patch.object(FOLIOService, "_request")
    @patch.object(FOLIOService, "get_user_by_cnetid")
    def test_sorts_by_expiration_date(self, mock_get_user, mock_request, mock_sp):
        mock_get_user.return_value = {"id": "uuid-1"}
        mock_sp.return_value = {}
        mock_request.return_value = {
            "requests": [
                {
                    "id": "req-2",
                    "instance": {"title": "Later Hold"},
                    "holdShelfExpirationDate": "2026-05-01",
                },
                {
                    "id": "req-1",
                    "instance": {"title": "Sooner Hold"},
                    "holdShelfExpirationDate": "2026-04-01",
                },
            ]
        }

        result = self.service.get_user_holds("testuser")

        self.assertEqual(result["holds"][0]["title"], "Sooner Hold")
        self.assertEqual(result["holds"][1]["title"], "Later Hold")


@override_settings(**FOLIO_SETTINGS)
class TestGetUserFines(TestCase):
    """Tests for FOLIOService.get_user_fines."""

    @classmethod
    def setUpTestData(cls):
        cls.service = FOLIOService()

    def setUp(self):
        cache.clear()

    @patch.object(FOLIOService, "_request")
    @patch.object(FOLIOService, "get_user_by_cnetid")
    def test_returns_fines_with_total(self, mock_get_user, mock_request):
        mock_get_user.return_value = {"id": "uuid-1"}
        mock_request.return_value = {
            "accounts": [
                {
                    "id": "fine-1",
                    "amount": 25.00,
                    "remaining": 25.00,
                    "feeFineType": "Overdue fine",
                    "title": "Late Book",
                    "metadata": {"createdDate": "2026-01-15"},
                },
            ]
        }

        result = self.service.get_user_fines("testuser")

        self.assertEqual(len(result["fines"]), 1)
        self.assertEqual(result["totalFines"], 1)
        self.assertEqual(result["fines"][0]["feeFineType"], "Overdue fine")

    @patch.object(FOLIOService, "_request")
    @patch.object(FOLIOService, "get_user_by_cnetid")
    def test_empty_fines(self, mock_get_user, mock_request):
        mock_get_user.return_value = {"id": "uuid-1"}
        mock_request.return_value = {"accounts": []}

        result = self.service.get_user_fines("testuser")

        self.assertEqual(result["fines"], [])
        self.assertEqual(result["totalAmount"], 0.0)
        self.assertEqual(result["totalFines"], 0)

    @patch.object(FOLIOService, "_request")
    @patch.object(FOLIOService, "get_user_by_cnetid")
    def test_calculates_total_amount(self, mock_get_user, mock_request):
        mock_get_user.return_value = {"id": "uuid-1"}
        mock_request.return_value = {
            "accounts": [
                {"id": "f1", "remaining": 10.50},
                {"id": "f2", "remaining": 5.25},
            ]
        }

        result = self.service.get_user_fines("testuser")
        self.assertAlmostEqual(result["totalAmount"], 15.75)


@override_settings(**FOLIO_SETTINGS)
class TestGetUserBlocks(TestCase):
    """Tests for FOLIOService.get_user_blocks."""

    @classmethod
    def setUpTestData(cls):
        cls.service = FOLIOService()

    def setUp(self):
        cache.clear()

    @patch.object(FOLIOService, "_request")
    @patch.object(FOLIOService, "get_user_by_cnetid")
    def test_returns_automated_blocks(self, mock_get_user, mock_request):
        mock_get_user.return_value = {"id": "uuid-1"}

        def side_effect(method, endpoint, **kwargs):
            if "automated-patron-blocks" in endpoint:
                return {
                    "automatedPatronBlocks": [
                        {
                            "message": "Too many overdue items",
                            "blockBorrowing": True,
                            "blockRenewals": False,
                            "blockRequests": False,
                        }
                    ]
                }
            elif "manualblocks" in endpoint:
                return {"manualblocks": []}
            return {}

        mock_request.side_effect = side_effect

        result = self.service.get_user_blocks("testuser")

        self.assertTrue(result["hasBlocks"])
        self.assertEqual(len(result["blocks"]), 1)
        self.assertEqual(result["blocks"][0]["type"], "automated")
        self.assertTrue(result["blocks"][0]["blockBorrowing"])

    @patch.object(FOLIOService, "_request")
    @patch.object(FOLIOService, "get_user_by_cnetid")
    def test_returns_manual_blocks(self, mock_get_user, mock_request):
        mock_get_user.return_value = {"id": "uuid-1"}

        def side_effect(method, endpoint, **kwargs):
            if "automated-patron-blocks" in endpoint:
                return {"automatedPatronBlocks": []}
            elif "manualblocks" in endpoint:
                return {
                    "manualblocks": [
                        {
                            "patronMessage": "Contact library",
                            "borrowing": True,
                            "renewals": True,
                            "requests": False,
                        }
                    ]
                }
            return {}

        mock_request.side_effect = side_effect

        result = self.service.get_user_blocks("testuser")

        self.assertTrue(result["hasBlocks"])
        self.assertEqual(result["blocks"][0]["type"], "manual")
        self.assertEqual(result["blocks"][0]["message"], "Contact library")

    @patch.object(FOLIOService, "_request")
    @patch.object(FOLIOService, "get_user_by_cnetid")
    def test_empty_blocks(self, mock_get_user, mock_request):
        mock_get_user.return_value = {"id": "uuid-1"}

        def side_effect(method, endpoint, **kwargs):
            if "automated-patron-blocks" in endpoint:
                return {"automatedPatronBlocks": []}
            elif "manualblocks" in endpoint:
                return {"manualblocks": []}
            return {}

        mock_request.side_effect = side_effect

        result = self.service.get_user_blocks("testuser")

        self.assertFalse(result["hasBlocks"])
        self.assertEqual(result["blocks"], [])

    @patch.object(FOLIOService, "_request")
    @patch.object(FOLIOService, "get_user_by_cnetid")
    def test_gracefully_handles_block_fetch_failure(self, mock_get_user, mock_request):
        mock_get_user.return_value = {"id": "uuid-1"}

        def side_effect(method, endpoint, **kwargs):
            if "automated-patron-blocks" in endpoint:
                raise FOLIOError("API error")
            elif "manualblocks" in endpoint:
                return {
                    "manualblocks": [
                        {"patronMessage": "Manual block", "borrowing": True}
                    ]
                }
            return {}

        mock_request.side_effect = side_effect

        with self.assertLogs("mylib_dashboard.services.folio", level="WARNING"):
            result = self.service.get_user_blocks("testuser")

        # Manual blocks still returned despite automated blocks failure
        self.assertEqual(len(result["blocks"]), 1)
        self.assertEqual(result["blocks"][0]["type"], "manual")


@override_settings(**FOLIO_SETTINGS)
class TestGetPagingRequests(TestCase):
    """Tests for FOLIOService.get_paging_requests."""

    @classmethod
    def setUpTestData(cls):
        cls.service = FOLIOService()

    def setUp(self):
        cache.clear()

    @patch.object(FOLIOService, "get_locations")
    @patch.object(FOLIOService, "get_service_points")
    @patch.object(FOLIOService, "_request")
    @patch.object(FOLIOService, "get_user_by_cnetid")
    def test_returns_paging_requests_with_locations(
        self, mock_get_user, mock_request, mock_sp, mock_loc
    ):
        mock_get_user.return_value = {"id": "uuid-1"}
        mock_sp.return_value = {"sp-1": "Regenstein Circ Desk"}
        mock_loc.return_value = {
            "loc-1": {"name": "Regenstein Stacks", "code": "reg", "libraryId": "lib-1"}
        }
        mock_request.return_value = {
            "requests": [
                {
                    "id": "page-1",
                    "instance": {"title": "Paged Book"},
                    "item": {
                        "callNumber": "QA76.73",
                        "locationId": "loc-1",
                    },
                    "pickupServicePointId": "sp-1",
                    "requestDate": "2026-03-10",
                    "status": "Open - Not yet filled",
                },
            ]
        }

        result = self.service.get_paging_requests("testuser")

        self.assertEqual(len(result["requests"]), 1)
        self.assertEqual(result["totalRequests"], 1)
        self.assertEqual(result["requests"][0]["title"], "Paged Book")
        self.assertEqual(result["requests"][0]["locationName"], "Regenstein Stacks")
        self.assertEqual(
            result["requests"][0]["pickupLocation"], "Regenstein Circ Desk"
        )

    @patch.object(FOLIOService, "get_locations")
    @patch.object(FOLIOService, "get_service_points")
    @patch.object(FOLIOService, "_request")
    @patch.object(FOLIOService, "get_user_by_cnetid")
    def test_empty_requests(self, mock_get_user, mock_request, mock_sp, mock_loc):
        mock_get_user.return_value = {"id": "uuid-1"}
        mock_sp.return_value = {}
        mock_loc.return_value = {}
        mock_request.return_value = {"requests": []}

        result = self.service.get_paging_requests("testuser")

        self.assertEqual(result["requests"], [])
        self.assertEqual(result["totalRequests"], 0)

    @patch.object(FOLIOService, "get_locations")
    @patch.object(FOLIOService, "get_service_points")
    @patch.object(FOLIOService, "_request")
    @patch.object(FOLIOService, "get_user_by_cnetid")
    def test_sorts_by_request_date(
        self, mock_get_user, mock_request, mock_sp, mock_loc
    ):
        mock_get_user.return_value = {"id": "uuid-1"}
        mock_sp.return_value = {}
        mock_loc.return_value = {}
        mock_request.return_value = {
            "requests": [
                {
                    "id": "page-2",
                    "instance": {"title": "Newer Request"},
                    "item": {},
                    "requestDate": "2026-03-12",
                },
                {
                    "id": "page-1",
                    "instance": {"title": "Older Request"},
                    "item": {},
                    "requestDate": "2026-03-10",
                },
            ]
        }

        result = self.service.get_paging_requests("testuser")

        self.assertEqual(result["requests"][0]["title"], "Older Request")
        self.assertEqual(result["requests"][1]["title"], "Newer Request")


class TestGetFolioServiceLruCache(TestCase):
    """Tests for get_folio_service LRU cache."""

    def tearDown(self):
        get_folio_service.cache_clear()

    @override_settings(**FOLIO_SETTINGS)
    def test_returns_same_instance(self):
        service1 = get_folio_service()
        service2 = get_folio_service()
        self.assertIs(service1, service2)
