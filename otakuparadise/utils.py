import logging

import requests

logger = logging.getLogger(__name__)


def api_get(url, params=None, timeout=10):
    """GET request with timeout, error handling, and safe JSON parsing."""
    try:
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.warning("API request failed for %s: %s", url, e)
        return {}
    except (ValueError, KeyError) as e:
        logger.warning("Invalid JSON from %s: %s", url, e)
        return {}


def safe_page(request):
    """Extract and validate the page number from a request."""
    try:
        page = int(request.GET.get("page", 1))
    except (ValueError, TypeError):
        page = 1
    return max(page, 1)
