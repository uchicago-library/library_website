"""
Aeon API service for Special Collections material requests.

Aeon is the system used by Special Collections for managing requests
to view archival materials by appointment.
"""

import logging
from functools import lru_cache

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class AeonError(Exception):
    """Base exception for Aeon API errors."""

    pass


class AeonService:
    """
    Client for the Aeon API.

    Handles authentication and requests to fetch Special Collections
    material requests.
    """

    def __init__(self):
        self.base_url = getattr(
            settings,
            "AEON_API_BASE_URL",
            "",
        )
        self.api_key = getattr(settings, "AEON_API_KEY", "")
        self.timeout = getattr(settings, "AEON_TIMEOUT", 30)

        if not self.api_key:
            logger.warning("AEON_API_KEY not configured")

    def _request(self, method, endpoint, **kwargs):
        """Make an authenticated request to the Aeon API."""
        url = f"{self.base_url}{endpoint}"
        headers = {
            "accept": "application/json;odata.metadata=minimal;odata.streaming=true",
            "X-AEON-API-KEY": self.api_key,
        }

        try:
            response = requests.request(
                method, url, headers=headers, timeout=self.timeout, **kwargs
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            logger.error(f"Aeon API timeout: {endpoint}")
            raise AeonError("Aeon API request timed out")
        except requests.exceptions.HTTPError as e:
            logger.error(f"Aeon API HTTP error: {e}")
            raise AeonError(f"Aeon API error: {e.response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Aeon API request failed: {e}")
            raise AeonError(f"Aeon API request failed: {e}")

    def get_user_requests(self, email):
        """
        Get all material requests for a user.

        Args:
            email: User's email address (used as Aeon username)

        Returns:
            dict with 'requests' array and 'totalRequests' count
        """
        endpoint = f"/Users/{email}/requests"
        try:
            data = self._request("GET", endpoint)
        except AeonError as e:
            # Aeon returns 404 when user has no active requests (bad API design)
            if "404" in str(e):
                return {"requests": [], "totalRequests": 0}
            raise

        # data is a list of requests
        requests_list = data if isinstance(data, list) else []

        # Transform to our standard format
        material_requests = []
        for req in requests_list:
            # Map transactionStatus codes to human-readable status
            status = self._map_status(req.get("transactionStatus"))

            material_requests.append(
                {
                    "id": str(req.get("transactionNumber")),
                    "title": req.get("itemTitle") or "Untitled",
                    "author": self._clean_author(req.get("itemAuthor")),
                    "callNumber": req.get("callNumber") or "",
                    "location": req.get("location") or "",
                    "subLocation": req.get("subLocation") or "",
                    "scheduledDate": req.get("scheduledDate"),
                    "requestDate": req.get("creationDate"),
                    "status": status,
                    "statusCode": req.get("transactionStatus"),
                    "specialRequest": req.get("specialRequest") or "",
                    "itemVolume": req.get("itemVolume") or "",
                }
            )

        # Sort by scheduled date (soonest first), then by request date
        material_requests.sort(
            key=lambda r: (r.get("scheduledDate") or "9999", r.get("requestDate") or "")
        )

        return {"requests": material_requests, "totalRequests": len(material_requests)}

    def _map_status(self, status_code):
        """
        Map Aeon transaction status codes to human-readable strings.

        Common status codes (may need adjustment based on actual Aeon config):
        - Awaiting Request Processing
        - In Retrieval
        - Paging
        - On Hold
        - Delivered to Reading Room
        - etc.
        """
        # These are common Aeon statuses - may need to be adjusted
        # based on UChicago's specific Aeon configuration
        status_map = {
            # Add specific mappings as we learn them
            # For now, return a generic "Processing" for unknown codes
        }
        return status_map.get(status_code, "Pending")

    def _clean_author(self, author):
        """Clean up author string (remove trailing commas, etc.)."""
        if not author:
            return ""
        # Remove trailing commas and extra whitespace
        return author.rstrip(",").strip()


@lru_cache(maxsize=1)
def get_aeon_service():
    """Get a cached AeonService instance."""
    return AeonService()
