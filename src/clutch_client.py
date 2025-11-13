import logging
from dataclasses import dataclass
from typing import Optional

import requests

@dataclass
class ClutchClient:
    timeout: float = 15.0
    max_retries: int = 3
    user_agent: str = "AdvancedClutchScraper/1.0"

    def __post_init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": self.user_agent,
                "Accept-Language": "en-US,en;q=0.9",
            }
        )

    def fetch_profile(self, url: str) -> Optional[str]:
        """Fetch a Clutch.co profile page and return its HTML."""
        for attempt in range(1, self.max_retries + 1):
            try:
                resp = self.session.get(url, timeout=self.timeout)
                if resp.status_code == 200:
                    self.logger.debug("Fetched %s (len=%d)", url, len(resp.text))
                    return resp.text

                self.logger.warning(
                    "Non-200 status for %s on attempt %d/%d: %s",
                    url,
                    attempt,
                    self.max_retries,
                    resp.status_code,
                )
            except requests.RequestException as exc:
                self.logger.warning(
                    "Request error for %s on attempt %d/%d: %s",
                    url,
                    attempt,
                    self.max_retries,
                    exc,
                )
        self.logger.error("Failed to fetch %s after %d attempts", url, self.max_retries)
        return None