"""Tests for mylib_dashboard.services.illiad."""

from unittest.mock import MagicMock, patch

import requests as real_requests
from django.test import TestCase, override_settings

from mylib_dashboard.services.illiad import (
    ILLiadError,
    ILLiadService,
    get_illiad_service,
)

ILLIAD_SETTINGS = {
    "ILLIAD_API_URL": "http://illiad.test/ILLiadWebPlatform",
    "ILLIAD_API_KEY": "test-api-key",
    "ILLIAD_TIMEOUT": 10,
    "ILLIAD_WEB_BASE_URL": "https://illiad.lib.uchicago.edu",
}


@override_settings(**ILLIAD_SETTINGS)
class TestILLiadServiceRequest(TestCase):
    """Tests for ILLiadService._request."""

    @classmethod
    def setUpTestData(cls):
        cls.service = ILLiadService()

    @patch("mylib_dashboard.services.illiad.requests")
    def test_successful_request(self, mock_requests):
        mock_response = MagicMock()
        mock_response.json.return_value = [{"TransactionNumber": 123}]
        mock_requests.get.return_value = mock_response

        result = self.service._request("/test-endpoint")

        self.assertEqual(result, [{"TransactionNumber": 123}])
        mock_requests.get.assert_called_once()

    @patch("mylib_dashboard.services.illiad.requests")
    def test_timeout_raises_error(self, mock_requests):
        mock_requests.get.side_effect = real_requests.exceptions.Timeout()
        mock_requests.exceptions = real_requests.exceptions

        with self.assertLogs("mylib_dashboard.services.illiad", level="ERROR"):
            with self.assertRaises(ILLiadError) as ctx:
                self.service._request("/test")
        self.assertIn("timed out", str(ctx.exception))

    @patch("mylib_dashboard.services.illiad.requests")
    def test_http_error_raises_error(self, mock_requests):
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_requests.get.side_effect = real_requests.exceptions.HTTPError(
            response=mock_resp
        )
        mock_requests.exceptions = real_requests.exceptions

        with self.assertLogs("mylib_dashboard.services.illiad", level="ERROR"):
            with self.assertRaises(ILLiadError) as ctx:
                self.service._request("/test")
        self.assertIn("500", str(ctx.exception))

    @patch("mylib_dashboard.services.illiad.requests")
    def test_request_exception_raises_error(self, mock_requests):
        mock_requests.get.side_effect = real_requests.exceptions.ConnectionError(
            "Connection refused"
        )
        mock_requests.exceptions = real_requests.exceptions

        with self.assertLogs("mylib_dashboard.services.illiad", level="ERROR"):
            with self.assertRaises(ILLiadError):
                self.service._request("/test")


@override_settings(**ILLIAD_SETTINGS)
class TestGetUserRequests(TestCase):
    """Tests for ILLiadService.get_user_requests."""

    @classmethod
    def setUpTestData(cls):
        cls.service = ILLiadService()

    # Filtering is done server-side by the ILLiad API, not in our code.
    # These tests verify that the correct params are passed to _request;
    # the different mock return values illustrate intent only.

    @patch.object(ILLiadService, "_request")
    def test_fetches_with_odata_filter(self, mock_request):
        mock_request.return_value = [{"TransactionNumber": 1}]

        result = self.service.get_user_requests("testuser", "Status eq 'Active'")

        mock_request.assert_called_once_with(
            "/Transaction/UserRequests/testuser",
            {"$filter": "Status eq 'Active'"},
        )
        self.assertEqual(len(result), 1)

    @patch.object(ILLiadService, "_request")
    def test_fetches_without_filter(self, mock_request):
        mock_request.return_value = [
            {"TransactionNumber": 1},
            {"TransactionNumber": 2},
        ]

        result = self.service.get_user_requests("testuser")

        mock_request.assert_called_once_with("/Transaction/UserRequests/testuser", {})
        self.assertEqual(len(result), 2)


@override_settings(**ILLIAD_SETTINGS)
class TestParseDate(TestCase):
    """Tests for ILLiadService._parse_date."""

    @classmethod
    def setUpTestData(cls):
        cls.service = ILLiadService()

    def test_parses_iso_date(self):
        result = self.service._parse_date("2026-01-15T10:00:00")
        self.assertIn("2026-01-15", result)

    def test_returns_none_for_empty(self):
        self.assertIsNone(self.service._parse_date(""))
        self.assertIsNone(self.service._parse_date(None))

    def test_returns_original_for_invalid(self):
        with self.assertLogs("mylib_dashboard.services.illiad", level="WARNING"):
            result = self.service._parse_date("not-a-date")
        self.assertEqual(result, "not-a-date")


@override_settings(**ILLIAD_SETTINGS)
class TestBuildDownloadUrl(TestCase):
    """Tests for ILLiadService._build_download_url."""

    @classmethod
    def setUpTestData(cls):
        cls.service = ILLiadService()

    def test_builds_url(self):
        transaction = {"TransactionNumber": 12345}
        url = self.service._build_download_url(transaction)
        self.assertEqual(
            url,
            "https://illiad.lib.uchicago.edu/illiad.dll?Action=10&Form=75&Value=12345",
        )

    def test_returns_empty_without_transaction_number(self):
        transaction = {}
        self.assertEqual(self.service._build_download_url(transaction), "")

    @override_settings(ILLIAD_WEB_BASE_URL="")
    def test_returns_empty_without_web_base_url(self):
        service = ILLiadService()
        transaction = {"TransactionNumber": 12345}
        self.assertEqual(service._build_download_url(transaction), "")


@override_settings(**ILLIAD_SETTINGS)
class TestFormatCopy(TestCase):
    """Tests for ILLiadService._format_copy."""

    @classmethod
    def setUpTestData(cls):
        cls.service = ILLiadService()

    def test_formats_copy_transaction(self):
        transaction = {
            "TransactionNumber": 100,
            "PhotoArticleTitle": "Test Article",
            "PhotoJournalTitle": "Test Journal",
            "PhotoArticleAuthor": "Author One",
            "TransactionStatus": "Delivered to Web",
            "CreationDate": "2026-01-10T09:00:00",
            "TransactionDate": "2026-01-12T15:00:00",
            "DueDate": "2026-02-10T00:00:00",
        }

        result = self.service._format_copy(transaction)

        self.assertEqual(result["id"], "100")
        self.assertEqual(result["articleTitle"], "Test Article")
        self.assertEqual(result["sourceTitle"], "Test Journal")
        self.assertEqual(result["author"], "Author One")
        self.assertEqual(result["status"], "Delivered to Web")
        self.assertIn("illiad.dll", result["downloadUrl"])


@override_settings(**ILLIAD_SETTINGS)
class TestFormatLoanRequest(TestCase):
    """Tests for ILLiadService._format_loan_request."""

    @classmethod
    def setUpTestData(cls):
        cls.service = ILLiadService()

    def test_formats_loan_request_transaction(self):
        transaction = {
            "TransactionNumber": 200,
            "LoanTitle": "Borrowed Book",
            "LoanAuthor": "Author Two",
            "TransactionStatus": "In Transit",
            "CreationDate": "2026-01-15T10:00:00",
            "TransactionDate": "2026-01-16T14:00:00",
            "DueDate": "2026-03-15T00:00:00",
            "RequestType": "Loan",
            "ProcessType": "Borrowing",
        }

        result = self.service._format_loan_request(transaction)

        self.assertEqual(result["id"], "200")
        self.assertEqual(result["title"], "Borrowed Book")
        self.assertEqual(result["author"], "Author Two")
        self.assertEqual(result["requestType"], "Loan")
        self.assertEqual(result["processType"], "Borrowing")


@override_settings(**ILLIAD_SETTINGS)
class TestGetCopiesReady(TestCase):
    """Tests for ILLiadService.get_copies_ready."""

    @classmethod
    def setUpTestData(cls):
        cls.service = ILLiadService()

    @patch.object(ILLiadService, "get_user_requests")
    def test_returns_formatted_copies(self, mock_get_requests):
        mock_get_requests.return_value = [
            {
                "TransactionNumber": 1,
                "PhotoArticleTitle": "Article 1",
                "PhotoJournalTitle": "Journal 1",
                "TransactionStatus": "Delivered to Web",
                "TransactionDate": "2026-01-10T10:00:00",
            },
        ]

        result = self.service.get_copies_ready("testuser")

        self.assertEqual(len(result["copies"]), 1)
        self.assertEqual(result["totalCopies"], 1)
        self.assertEqual(result["copies"][0]["articleTitle"], "Article 1")

    @patch.object(ILLiadService, "get_user_requests")
    def test_sorts_by_transaction_date_desc(self, mock_get_requests):
        mock_get_requests.return_value = [
            {
                "TransactionNumber": 1,
                "TransactionDate": "2026-01-05T10:00:00",
                "TransactionStatus": "Delivered to Web",
            },
            {
                "TransactionNumber": 2,
                "TransactionDate": "2026-01-10T10:00:00",
                "TransactionStatus": "Delivered to Web",
            },
        ]

        result = self.service.get_copies_ready("testuser")

        # Most recent first
        self.assertEqual(result["copies"][0]["id"], "2")
        self.assertEqual(result["copies"][1]["id"], "1")


@override_settings(**ILLIAD_SETTINGS)
class TestGetIllInProcess(TestCase):
    """Tests for ILLiadService.get_ill_in_process."""

    @classmethod
    def setUpTestData(cls):
        cls.service = ILLiadService()

    @patch.object(ILLiadService, "get_user_requests")
    def test_returns_formatted_requests(self, mock_get_requests):
        mock_get_requests.return_value = [
            {
                "TransactionNumber": 300,
                "LoanTitle": "ILL Book",
                "LoanAuthor": "ILL Author",
                "TransactionStatus": "Awaiting Lending Request Processing",
                "CreationDate": "2026-02-01T10:00:00",
                "ProcessType": "Borrowing",
                "RequestType": "Loan",
            },
        ]

        result = self.service.get_ill_in_process("testuser")

        self.assertEqual(len(result["requests"]), 1)
        self.assertEqual(result["totalRequests"], 1)
        self.assertEqual(result["requests"][0]["title"], "ILL Book")

    @patch.object(ILLiadService, "get_user_requests")
    def test_sorts_by_request_date_asc(self, mock_get_requests):
        mock_get_requests.return_value = [
            {
                "TransactionNumber": 2,
                "CreationDate": "2026-02-10T10:00:00",
                "ProcessType": "Borrowing",
            },
            {
                "TransactionNumber": 1,
                "CreationDate": "2026-02-01T10:00:00",
                "ProcessType": "Borrowing",
            },
        ]

        result = self.service.get_ill_in_process("testuser")

        # Oldest first
        self.assertEqual(result["requests"][0]["id"], "1")
        self.assertEqual(result["requests"][1]["id"], "2")


@override_settings(**ILLIAD_SETTINGS)
class TestGetScanDeliverInProcess(TestCase):
    """Tests for ILLiadService.get_scan_deliver_in_process."""

    @classmethod
    def setUpTestData(cls):
        cls.service = ILLiadService()

    @patch.object(ILLiadService, "get_user_requests")
    def test_returns_formatted_requests(self, mock_get_requests):
        mock_get_requests.return_value = [
            {
                "TransactionNumber": 400,
                "PhotoArticleTitle": "Scan Article",
                "PhotoJournalTitle": "Scan Journal",
                "TransactionStatus": "Awaiting DocDel Processing",
                "CreationDate": "2026-02-05T10:00:00",
                "ProcessType": "DocDel",
            },
        ]

        result = self.service.get_scan_deliver_in_process("testuser")

        self.assertEqual(len(result["requests"]), 1)
        self.assertEqual(result["totalRequests"], 1)
        self.assertEqual(result["requests"][0]["articleTitle"], "Scan Article")

    @patch.object(ILLiadService, "get_user_requests")
    def test_sorts_by_request_date_asc(self, mock_get_requests):
        mock_get_requests.return_value = [
            {
                "TransactionNumber": 2,
                "CreationDate": "2026-02-10T10:00:00",
                "ProcessType": "DocDel",
            },
            {
                "TransactionNumber": 1,
                "CreationDate": "2026-02-01T10:00:00",
                "ProcessType": "DocDel",
            },
        ]

        result = self.service.get_scan_deliver_in_process("testuser")

        # Oldest first
        self.assertEqual(result["requests"][0]["id"], "1")
        self.assertEqual(result["requests"][1]["id"], "2")


class TestGetIlliadServiceLruCache(TestCase):
    """Tests for get_illiad_service LRU cache."""

    def tearDown(self):
        get_illiad_service.cache_clear()

    @override_settings(**ILLIAD_SETTINGS)
    def test_returns_same_instance(self):
        service1 = get_illiad_service()
        service2 = get_illiad_service()
        self.assertIs(service1, service2)
