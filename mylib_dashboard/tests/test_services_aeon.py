"""Tests for mylib_dashboard.services.aeon."""

import logging
from unittest.mock import MagicMock, patch

import requests as real_requests
from django.test import TestCase, override_settings

from mylib_dashboard.services.aeon import AeonError, AeonService, get_aeon_service

AEON_SETTINGS = {
    "AEON_API_BASE_URL": "http://aeon.test",
    "AEON_API_KEY": "test-aeon-key",
    "AEON_TIMEOUT": 10,
}


@override_settings(**AEON_SETTINGS)
class TestAeonServiceInit(TestCase):
    """Tests for AeonService.__init__."""

    @override_settings(AEON_API_KEY="")
    def test_warns_when_no_api_key(self):
        with self.assertLogs("mylib_dashboard.services.aeon", level="WARNING") as logs:
            AeonService()
        self.assertTrue(any("AEON_API_KEY" in msg for msg in logs.output))


@override_settings(**AEON_SETTINGS)
class TestAeonServiceRequest(TestCase):
    """Tests for AeonService._request."""

    @classmethod
    def setUpTestData(cls):
        cls.service = AeonService()

    @patch("mylib_dashboard.services.aeon.requests")
    def test_successful_request(self, mock_requests):
        mock_response = MagicMock()
        mock_response.json.return_value = [{"transactionNumber": 1}]
        mock_requests.request.return_value = mock_response

        result = self.service._request("GET", "/test")

        self.assertEqual(result, [{"transactionNumber": 1}])

    @patch("mylib_dashboard.services.aeon.requests")
    def test_timeout_raises_error(self, mock_requests):

        mock_requests.request.side_effect = real_requests.exceptions.Timeout()
        mock_requests.exceptions = real_requests.exceptions

        with self.assertLogs("mylib_dashboard.services.aeon", level="ERROR"):
            with self.assertRaises(AeonError) as ctx:
                self.service._request("GET", "/test")
        self.assertIn("timed out", str(ctx.exception))

    @patch("mylib_dashboard.services.aeon.requests")
    def test_http_error_raises_error(self, mock_requests):

        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_requests.request.side_effect = real_requests.exceptions.HTTPError(
            response=mock_resp
        )
        mock_requests.exceptions = real_requests.exceptions

        with self.assertLogs("mylib_dashboard.services.aeon", level="ERROR"):
            with self.assertRaises(AeonError) as ctx:
                self.service._request("GET", "/test")
        self.assertIn("500", str(ctx.exception))

    @patch("mylib_dashboard.services.aeon.requests")
    def test_request_exception_raises_error(self, mock_requests):

        mock_requests.request.side_effect = real_requests.exceptions.ConnectionError(
            "Connection refused"
        )
        mock_requests.exceptions = real_requests.exceptions

        with self.assertLogs("mylib_dashboard.services.aeon", level="ERROR"):
            with self.assertRaises(AeonError):
                self.service._request("GET", "/test")


@override_settings(**AEON_SETTINGS)
class TestGetUserRequests(TestCase):
    """Tests for AeonService.get_user_requests."""

    def setUp(self):
        self.service = AeonService()

    @patch.object(AeonService, "_request")
    def test_returns_formatted_requests(self, mock_request):
        mock_request.side_effect = lambda method, endpoint: {
            "/Queues": [
                {"queue": {"id": 10, "queueName": "In Retrieval"}, "requestCount": 0}
            ],
            "/Users/user@uchicago.edu/requests": [
                {
                    "transactionNumber": 1001,
                    "itemTitle": "Archival Collection",
                    "itemAuthor": "Smith, John,",
                    "callNumber": "MS 123",
                    "location": "Regenstein",
                    "subLocation": "Floor 4",
                    "scheduledDate": "2026-03-20",
                    "creationDate": "2026-03-10",
                    "transactionStatus": 10,
                    "specialRequest": "Pages 1-50",
                    "itemVolume": "Box 2",
                },
            ],
        }[endpoint]

        result = self.service.get_user_requests("user@uchicago.edu")

        self.assertEqual(len(result["requests"]), 1)
        self.assertEqual(result["totalRequests"], 1)
        req = result["requests"][0]
        self.assertEqual(req["id"], "1001")
        self.assertEqual(req["title"], "Archival Collection")
        self.assertEqual(req["author"], "Smith, John")  # Trailing comma stripped
        self.assertEqual(req["callNumber"], "MS 123")
        self.assertEqual(req["status"], "In Retrieval")

    @patch.object(AeonService, "_request")
    def test_404_returns_empty_list(self, mock_request):
        mock_request.side_effect = AeonError("Aeon API error: 404")

        result = self.service.get_user_requests("user@uchicago.edu")

        self.assertEqual(result["requests"], [])
        self.assertEqual(result["totalRequests"], 0)

    @patch.object(AeonService, "_request")
    def test_sorts_by_scheduled_then_request_date(self, mock_request):
        mock_request.side_effect = lambda method, endpoint: {
            "/Queues": [
                {"queue": {"id": 10, "queueName": "New Request"}, "requestCount": 0}
            ],
            "/Users/user@uchicago.edu/requests": [
                {
                    "transactionNumber": 2,
                    "itemTitle": "Later Scheduled",
                    "scheduledDate": "2026-04-01",
                    "creationDate": "2026-03-01",
                    "transactionStatus": 10,
                },
                {
                    "transactionNumber": 1,
                    "itemTitle": "Sooner Scheduled",
                    "scheduledDate": "2026-03-20",
                    "creationDate": "2026-03-05",
                    "transactionStatus": 10,
                },
            ],
        }[endpoint]

        result = self.service.get_user_requests("user@uchicago.edu")

        self.assertEqual(result["requests"][0]["title"], "Sooner Scheduled")
        self.assertEqual(result["requests"][1]["title"], "Later Scheduled")

    @patch.object(AeonService, "_request")
    def test_filters_out_awaiting_user_review(self, mock_request):
        mock_request.side_effect = lambda method, endpoint: {
            "/Queues": [
                {
                    "queue": {"id": 5, "queueName": "Awaiting User Review"},
                    "requestCount": 0,
                },
                {"queue": {"id": 10, "queueName": "In Retrieval"}, "requestCount": 0},
            ],
            "/Users/user@uchicago.edu/requests": [
                {
                    "transactionNumber": 1,
                    "itemTitle": "Active Request",
                    "scheduledDate": "2026-03-20",
                    "creationDate": "2026-03-10",
                    "transactionStatus": 10,
                },
                {
                    "transactionNumber": 2,
                    "itemTitle": "Saved For Later",
                    "scheduledDate": "2026-04-01",
                    "creationDate": "2026-03-15",
                    "transactionStatus": 5,
                },
            ],
        }[endpoint]

        result = self.service.get_user_requests("user@uchicago.edu")

        self.assertEqual(len(result["requests"]), 1)
        self.assertEqual(result["totalRequests"], 1)
        self.assertEqual(result["requests"][0]["title"], "Active Request")

    @patch.object(AeonService, "_request")
    def test_handles_non_list_response(self, mock_request):
        mock_request.side_effect = lambda method, endpoint: (
            [] if endpoint == "/Queues" else {"error": "something"}
        )

        result = self.service.get_user_requests("user@uchicago.edu")

        self.assertEqual(result["requests"], [])
        self.assertEqual(result["totalRequests"], 0)


@override_settings(**AEON_SETTINGS)
class TestGetQueueMap(TestCase):
    """Tests for AeonService._get_queue_map and _map_status."""

    def setUp(self):
        self.service = AeonService()

    @patch.object(AeonService, "_request")
    def test_prefers_display_name_over_queue_name(self, mock_request):
        mock_request.return_value = [
            {
                "queue": {
                    "id": 57,
                    "queueName": "New Request with Special Request Note",
                    "displayName": "New Request",
                },
                "requestCount": 0,
            },
        ]

        self.assertEqual(self.service._map_status(57), "New Request")

    @patch.object(AeonService, "_request")
    def test_falls_back_to_queue_name_when_no_display_name(self, mock_request):
        mock_request.return_value = [
            {
                "queue": {
                    "id": 38,
                    "queueName": "Awaiting Future Request Processing",
                    "displayName": None,
                },
                "requestCount": 0,
            },
        ]

        self.assertEqual(
            self.service._map_status(38), "Awaiting Future Request Processing"
        )

    @patch.object(AeonService, "_request")
    def test_returns_fallback_for_unknown_code(self, mock_request):
        mock_request.return_value = [
            {"queue": {"id": 1, "queueName": "New Request"}, "requestCount": 0}
        ]

        self.assertEqual(self.service._map_status(999), "Status 999")

    @patch.object(AeonService, "_request")
    def test_caches_queue_map(self, mock_request):
        mock_request.return_value = [
            {"queue": {"id": 1, "queueName": "New Request"}, "requestCount": 0}
        ]

        self.service._map_status(1)
        self.service._map_status(1)

        mock_request.assert_called_once_with("GET", "/Queues")

    @patch.object(AeonService, "_request")
    def test_handles_queue_fetch_failure(self, mock_request):
        mock_request.side_effect = AeonError("Aeon API error: 500")

        with self.assertLogs("mylib_dashboard.services.aeon", level="WARNING"):
            result = self.service._map_status(38)

        self.assertEqual(result, "Status 38")


@override_settings(**AEON_SETTINGS)
class TestCleanAuthor(TestCase):
    """Tests for AeonService._clean_author."""

    @classmethod
    def setUpTestData(cls):
        cls.service = AeonService()

    def test_strips_trailing_comma(self):
        self.assertEqual(self.service._clean_author("Smith, John,"), "Smith, John")

    def test_returns_empty_for_none(self):
        self.assertEqual(self.service._clean_author(None), "")
        self.assertEqual(self.service._clean_author(""), "")


class TestGetAeonServiceLruCache(TestCase):
    """Tests for get_aeon_service LRU cache."""

    def tearDown(self):
        get_aeon_service.cache_clear()

    @override_settings(**AEON_SETTINGS)
    def test_returns_same_instance(self):
        # Suppress the warning about missing API key if it fires
        logging.disable(logging.WARNING)
        try:
            service1 = get_aeon_service()
            service2 = get_aeon_service()
            self.assertIs(service1, service2)
        finally:
            logging.disable(logging.NOTSET)
