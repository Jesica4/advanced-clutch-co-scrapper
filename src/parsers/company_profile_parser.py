from __future__ import annotations

import logging
from typing import Any, Dict, List

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

def _get_meta(soup: BeautifulSoup, prop: str, attr: str = "property") -> str | None:
    tag = soup.find("meta", {attr: prop})
    if tag and tag.get("content"):
        return tag["content"].strip()
    return None

def parse_company_profile(html: str, url: str) -> Dict[str, Any]:
    """Parse high-level company profile information from a Clutch.co HTML page.

    This parser is intentionally resilient: it relies on Open Graph tags and common
    layout patterns so it continues working even if the page structure changes.
    """
    soup = BeautifulSoup(html, "html.parser")

    og_title = _get_meta(soup, "og:title")
    og_description = _get_meta(soup, "og:description")
    og_url = _get_meta(soup, "og:url")
    og_image = _get_meta(soup, "og:image")
    og_site_name = _get_meta(soup, "og:site_name")

    # Name / tagline fallbacks
    h1 = soup.find("h1")
    headline_text = h1.get_text(strip=True) if h1 else None

    name = og_title or headline_text or og_site_name or "Unknown Company"

    # Rating and review count: try schema.org AggregateRating if present
    rating_value = None
    rating_count = None
    aggregate_rating = soup.find(attrs={"itemtype": "http://schema.org/AggregateRating"})
    if aggregate_rating:
        rating_value_tag = aggregate_rating.find(attrs={"itemprop": "ratingValue"})
        rating_count_tag = aggregate_rating.find(attrs={"itemprop": "reviewCount"})
        if rating_value_tag:
            rating_value = rating_value_tag.get_text(strip=True)
        if rating_count_tag:
            rating_count = rating_count_tag.get_text(strip=True)

    summary: Dict[str, Any] = {
        "name": name,
        "logo": og_image,
        "tagLine": None,
        "description": og_description,
        "totalReview": rating_count,
        "rating": rating_value,
        "verificationStatus": None,
        "minProjectSize": None,
        "averageHourlyRate": None,
        "employees": None,
        "founded": None,
        "video_url": None,
        "languages": [],  # type: List[str]
        "timezones": [],  # type: List[str]
    }

    # Basic extraction of tagline / description from known selectors
    tagline_node = soup.select_one(".provider-heading h2, .summary__tagline, .tagline")
    if tagline_node:
        summary["tagLine"] = tagline_node.get_text(strip=True)

    long_description_node = soup.select_one(
        ".summary-description, .provider-description, [data-role='description']"
    )
    if long_description_node:
        text = long_description_node.get_text(separator=" ", strip=True)
        if text:
            summary["description"] = text

    # Simple extraction of "founded" info if it appears as text
    founded_candidates = soup.find_all(string=lambda s: s and "Founded" in s)
    for candidate in founded_candidates:
        text = candidate.strip()
        if "Founded" in text:
            summary["founded"] = text
            break

    # Addresses: we keep this generic, since Clutch layout may change.
    addresses: List[Dict[str, Any]] = []
    address_blocks = soup.select("[itemtype='http://schema.org/PostalAddress']")
    for block in address_blocks:
        def safe_get(itemprop: str) -> str | None:
            el = block.find(attrs={"itemprop": itemprop})
            return el.get_text(strip=True) if el else None

        address = {
            "title": None,
            "streetAddress": safe_get("streetAddress"),
            "locality": safe_get("addressLocality"),
            "region": safe_get("addressRegion"),
            "country": safe_get("addressCountry"),
            "postalCode": safe_get("postalCode"),
            "locationEmployees": None,
            "telephone": None,
        }
        if any(address.values()):
            addresses.append(address)

    # Extract top-level website URL if provided
    website_url = None
    website_link = soup.select_one("a[href^='http']:not([href*='clutch.co'])")
    if website_link:
        website_url = website_link.get("href")

    # Aggregate rating block, if present
    rating = {
        "totalReview": summary["totalReview"],
        "overallRating": summary["rating"],
    }

    data: Dict[str, Any] = {
        "summary": summary,
        "addresses": addresses,
        "verification": {
            "businessEntity": {},
            "paymentLegalFilings": {},
        },
        "chartPie": {
            "service_provided": {"legend_title": "Service Lines", "slices": []},
            "focus": {"charts": {}},
            "industries": {"slices": []},
            "clients": {"slices": []},
        },
        "rating": rating,
        "websiteUrl": website_url,
        "profileURL": og_url or url,
        "reviewInsights": {
            "topMentions": [],
            "reviewHighlights": [],
        },
    }

    logger.debug("Parsed profile for %s: %s", url, data["summary"])
    return data