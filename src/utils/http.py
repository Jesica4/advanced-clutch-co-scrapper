from __future__ import annotations

import logging
from typing import Optional

import requests

logger = logging.getLogger(__name__)

def http_get(
    url: str,
    *,
    session: Optional[requests.Session] = None,
    timeout: float = 15.0,
    max_retries: int = 3,
) -> Optional[str]:
    """Thin wrapper around requests.get with retries and logging."""
    sess = session or requests.Session()
    for attempt in range(1, max_retries + 1):
        try:
            resp = sess.get(url, timeout=timeout)
            if resp.status_code == 200:
                logger.debug("Fetched %s (len=%d)", url, len(resp.text))
                return resp.text

            logger.warning(
                "Attempt %d/%d for %s returned %d",
                attempt,
                max_retries,
                url,
                resp.status_code,
            )
        except requests.RequestException as exc:
            logger.warning(
                "Attempt %d/%d for %s failed: %s",
                attempt,
                max_retries,
                url,
                exc,
            )
    logger.error("Failed to fetch %s after %d attempts", url, max_retries)
    return None