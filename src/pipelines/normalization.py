from __future__ import annotations

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

def normalize_company_data(
    profile_data: Dict[str, Any],
    reviews: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Attach reviews and compute a few derived fields on top of profile data.

    The goal is not to perfectly replicate Clutch's internal schema but to
    produce a predictable, analytics-friendly JSON structure.
    """
    result = dict(profile_data)  # shallow copy

    # Attach reviews
    result["reviews"] = reviews

    # Recompute rating aggregates if possible
    numeric_ratings = [
        r.get("review", {}).get("rating")
        for r in reviews
        if isinstance(r.get("review", {}).get("rating"), (int, float))
    ]
    if numeric_ratings:
        avg_rating = round(sum(numeric_ratings) / len(numeric_ratings), 2)
        rating_block = result.get("rating") or {}
        rating_block["overallRating"] = str(avg_rating)
        rating_block["totalReview"] = str(len(numeric_ratings))
        result["rating"] = rating_block

    logger.debug(
        "Normalized company data for %s with %d reviews",
        result.get("profileURL"),
        len(reviews),
    )
    return result