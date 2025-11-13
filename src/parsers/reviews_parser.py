from __future__ import annotations

import logging
from typing import Any, Dict, List

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

def parse_reviews(html: str) -> List[Dict[str, Any]]:
    """Parse reviews from a Clutch.co company profile HTML page.

    We primarily look for schema.org Review microdata, but this parser is
    defensive and falls back to common CSS patterns when needed.
    """
    soup = BeautifulSoup(html, "html.parser")
    reviews: List[Dict[str, Any]] = []

    # Prefer schema.org Review microdata
    review_nodes = soup.find_all(attrs={"itemtype": "http://schema.org/Review"})
    for node in review_nodes:
        review = _parse_schema_org_review(node)
        if review:
            reviews.append(review)

    # If none found, fall back to common review card selectors
    if not reviews:
        for block in soup.select(".review-card, .review-card__inner, .review"):
            review = _parse_review_block(block)
            if review:
                reviews.append(review)

    logger.debug("Parsed %d reviews from page", len(reviews))
    return reviews

def _parse_schema_org_review(node) -> Dict[str, Any] | None:
    """Parse a single schema.org Review node into our normalized structure."""
    try:
        def text_of(itemprop: str) -> str | None:
            el = node.find(attrs={"itemprop": itemprop})
            return el.get_text(strip=True) if el else None

        name = text_of("name") or text_of("headline")
        date_published = text_of("datePublished")

        rating_value = None
        review_rating = node.find(attrs={"itemprop": "reviewRating"})
        if review_rating:
            rating_el = review_rating.find(attrs={"itemprop": "ratingValue"})
            rating_value = rating_el.get_text(strip=True) if rating_el else None

        body = text_of("reviewBody")

        reviewer_block = node.find(attrs={"itemprop": "author"})
        reviewer = {}
        if reviewer_block:
            reviewer["name"] = reviewer_block.get_text(strip=True)

        return {
            "name": name,
            "datePublished": date_published,
            "project": {
                "name": None,
                "categories": [],
                "budget": None,
                "length": None,
                "description": None,
            },
            "review": {
                "rating": float(rating_value) if rating_value else None,
                "quality": None,
                "schedule": None,
                "cost": None,
                "willingToRefer": None,
                "review": body,
                "comments": body,
            },
            "reviewer": reviewer,
        }
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to parse schema.org review: %s", exc)
        return None

def _parse_review_block(block) -> Dict[str, Any] | None:
    """Fallback parser for non-schema review cards."""
    try:
        title = block.select_one(".review-title, h3, h2")
        meta_date = block.select_one(".review-date, time")
        rating_el = block.select_one(".rating, .stars, [data-rating]")

        rating_value = None
        if rating_el and rating_el.has_attr("data-rating"):
            rating_value = rating_el["data-rating"]
        elif rating_el:
            rating_value = rating_el.get_text(strip=True)

        text_node = block.select_one(".review-text, .content, p")
        text = text_node.get_text(strip=True) if text_node else None

        reviewer_name_el = block.select_one(
            ".reviewer-name, .author, .client, .reviewer"
        )
        reviewer_name = (
            reviewer_name_el.get_text(strip=True) if reviewer_name_el else None
        )

        return {
            "name": title.get_text(strip=True) if title else None,
            "datePublished": meta_date.get_text(strip=True) if meta_date else None,
            "project": {
                "name": None,
                "categories": [],
                "budget": None,
                "length": None,
                "description": None,
            },
            "review": {
                "rating": float(rating_value) if rating_value else None,
                "quality": None,
                "schedule": None,
                "cost": None,
                "willingToRefer": None,
                "review": text,
                "comments": text,
            },
            "reviewer": {
                "name": reviewer_name,
            },
        }
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to parse review block: %s", exc)
        return None