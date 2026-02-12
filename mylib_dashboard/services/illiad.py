"""
ILLiad API Service for MyLib Dashboard.

Handles interlibrary loan and scan & deliver data retrieval from ILLiad.
"""

import logging
from datetime import datetime
from functools import lru_cache

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 30


class ILLiadError(Exception):
    """Base exception for ILLiad API errors."""

    pass


class ILLiadService:
    """
    Service for interacting with the ILLiad Web Platform API.
    Uses API key authentication.
    """

    def __init__(self):
        self.base_url = getattr(settings, "ILLIAD_API_URL", "").rstrip("/")
        self.api_key = getattr(settings, "ILLIAD_API_KEY", "")
        self.timeout = getattr(settings, "ILLIAD_TIMEOUT", DEFAULT_TIMEOUT)

    def _get_headers(self):
        """Build headers for ILLiad API requests."""
        return {
            "ApiKey": self.api_key,
            "Accept": "application/json",
        }

    def _request(self, endpoint, params=None):
        """
        Make an authenticated GET request to ILLiad.

        Args:
            endpoint: API endpoint (without base URL)
            params: Optional query parameters (for OData $filter, etc.)

        Returns:
            list or dict: JSON response

        Raises:
            ILLiadError: If the request fails
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()

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
            logger.error(f"ILLiad request timed out: {endpoint}")
            raise ILLiadError("Request to ILLiad timed out")
        except requests.exceptions.HTTPError as e:
            logger.error(f"ILLiad request failed: {endpoint} - {e}")
            raise ILLiadError(f"ILLiad request failed: {e.response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"ILLiad request error: {endpoint} - {e}")
            raise ILLiadError(f"ILLiad request failed: {e}")

    def get_user_requests(self, cnetid, odata_filter=None):
        """
        Get ILLiad requests for a user.

        Args:
            cnetid: The user's CNetID (ILLiad username)
            odata_filter: Optional OData $filter string

        Returns:
            list: List of transaction objects from ILLiad
        """
        endpoint = f"/Transaction/UserRequests/{cnetid}"
        params = {}
        if odata_filter:
            params["$filter"] = odata_filter

        return self._request(endpoint, params)

    def _parse_date(self, date_str):
        """Parse ILLiad date string to ISO format."""
        if not date_str:
            return None
        try:
            # ILLiad returns dates like "2026-01-15T10:00:00"
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return dt.isoformat()
        except (ValueError, AttributeError):
            logger.warning(f"Could not parse ILLiad date: {date_str}")
            return date_str

    def _build_download_url(self, transaction):
        """
        Build the PDF download URL for a transaction.

        Constructs URL from TransactionNumber using the configured
        ILLiad web base URL.

        Args:
            transaction: The transaction object from ILLiad

        Returns:
            str: The download URL, or empty string if unavailable
        """
        transaction_number = transaction.get("TransactionNumber")
        if not transaction_number:
            return ""

        # Get base URL from settings
        # URL pattern: {base}/illiad.dll?Action=10&Form=75&Value={TransactionNumber}
        web_base = getattr(settings, "ILLIAD_WEB_BASE_URL", "").rstrip("/")
        if not web_base:
            return ""

        return f"{web_base}/illiad.dll?Action=10&Form=75&Value={transaction_number}"

    def _format_copy(self, transaction):
        """
        Format a copy/article transaction for the frontend.

        Args:
            transaction: The transaction object from ILLiad

        Returns:
            dict: Formatted copy data
        """
        return {
            "id": str(transaction.get("TransactionNumber", "")),
            "articleTitle": transaction.get("PhotoArticleTitle", ""),
            "sourceTitle": transaction.get("PhotoJournalTitle", ""),
            "author": transaction.get("PhotoArticleAuthor", ""),
            "status": transaction.get("TransactionStatus", ""),
            "requestDate": self._parse_date(transaction.get("CreationDate")),
            "transactionDate": self._parse_date(transaction.get("TransactionDate")),
            "downloadUrl": self._build_download_url(transaction),
            "dueDate": self._parse_date(transaction.get("DueDate")),
        }

    def _format_loan_request(self, transaction):
        """
        Format a loan/physical item transaction for the frontend.

        Args:
            transaction: The transaction object from ILLiad

        Returns:
            dict: Formatted loan request data
        """
        return {
            "id": str(transaction.get("TransactionNumber", "")),
            "title": transaction.get("LoanTitle", ""),
            "author": transaction.get("LoanAuthor", ""),
            "status": transaction.get("TransactionStatus", ""),
            "requestDate": self._parse_date(transaction.get("CreationDate")),
            "transactionDate": self._parse_date(transaction.get("TransactionDate")),
            "dueDate": self._parse_date(transaction.get("DueDate")),
            "requestType": transaction.get("RequestType", ""),
            "processType": transaction.get("ProcessType", ""),
        }

    def get_copies_ready(self, cnetid):
        """
        Get Scan & Deliver copies ready for download.

        These are article/chapter requests that have been delivered electronically.

        Args:
            cnetid: The user's CNetID

        Returns:
            dict: {
                "copies": [...],
                "totalCopies": int,
            }
        """
        # Filter for Article requests that have been delivered to web
        odata_filter = "TransactionStatus eq 'Delivered to Web'"

        try:
            transactions = self.get_user_requests(cnetid, odata_filter)
        except ILLiadError:
            raise

        copies = [self._format_copy(t) for t in transactions]

        # Sort by transaction date (most recent first)
        copies.sort(key=lambda c: c.get("transactionDate") or "", reverse=True)

        return {
            "copies": copies,
            "totalCopies": len(copies),
        }

    def get_ill_in_process(self, cnetid):
        """
        Get ILL requests that are being processed (physical items from other libraries).

        Args:
            cnetid: The user's CNetID

        Returns:
            dict: {
                "requests": [...],
                "totalRequests": int,
            }
        """
        # Filter for Borrowing process type (ILL from external libraries)
        # Exclude completed/cancelled statuses
        odata_filter = (
            "ProcessType eq 'Borrowing' and "
            "TransactionStatus ne 'Request Finished' and "
            "TransactionStatus ne 'Cancelled by ILL Staff' and "
            "TransactionStatus ne 'Cancelled by Customer' and "
            "TransactionStatus ne 'Delivered to Web' and "
            "TransactionStatus ne 'Checked Out to Customer'"
        )

        try:
            transactions = self.get_user_requests(cnetid, odata_filter)
        except ILLiadError:
            raise

        requests_list = [self._format_loan_request(t) for t in transactions]

        # Sort by request date (oldest first - longest waiting)
        requests_list.sort(key=lambda r: r.get("requestDate") or "")

        return {
            "requests": requests_list,
            "totalRequests": len(requests_list),
        }

    def get_scan_deliver_in_process(self, cnetid):
        """
        Get Scan & Deliver requests that are being processed.

        These are article/chapter scans from UChicago's own collection.

        Args:
            cnetid: The user's CNetID

        Returns:
            dict: {
                "requests": [...],
                "totalRequests": int,
            }
        """
        # Filter for DocDel process type (Scan & Deliver from our collection)
        # Exclude completed/cancelled statuses
        odata_filter = (
            "ProcessType eq 'DocDel' and "
            "TransactionStatus ne 'Request Finished' and "
            "TransactionStatus ne 'Cancelled by ILL Staff' and "
            "TransactionStatus ne 'Cancelled by Customer' and "
            "TransactionStatus ne 'Delivered to Web'"
        )

        try:
            transactions = self.get_user_requests(cnetid, odata_filter)
        except ILLiadError:
            raise

        requests_list = [self._format_copy(t) for t in transactions]

        # Sort by request date (oldest first - longest waiting)
        requests_list.sort(key=lambda r: r.get("requestDate") or "")

        return {
            "requests": requests_list,
            "totalRequests": len(requests_list),
        }


@lru_cache(maxsize=1)
def get_illiad_service():
    """Get a cached ILLiadService instance."""
    return ILLiadService()
