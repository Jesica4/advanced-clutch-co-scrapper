import sys
from pathlib import Path

# Ensure src/ is importable
ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from pipelines.normalization import normalize_company_data

def test_normalization_aggregates_rating():
    profile_data = {
        "summary": {
            "name": "Demo Company",
            "logo": None,
            "tagLine": None,
            "description": None,
            "totalReview": None,
            "rating": None,
            "verificationStatus": None,
            "minProjectSize": None,
            "averageHourlyRate": None,
            "employees": None,
            "founded": None,
            "video_url": None,
            "languages": [],
            "timezones": [],
        },
        "addresses": [],
        "verification": {"businessEntity": {}, "paymentLegalFilings": {}},
        "chartPie": {
            "service_provided": {"legend_title": "Service Lines", "slices": []},
            "focus": {"charts": {}},
            "industries": {"slices": []},
            "clients": {"slices": []},
        },
        "rating": {"totalReview": None, "overallRating": None},
        "websiteUrl": "https://example.com",
        "profileURL": "https://clutch.co/profile/demo-company",
        "reviewInsights": {"topMentions": [], "reviewHighlights": []},
    }

    reviews = [
        {"review": {"rating": 5}},
        {"review": {"rating": 4.5}},
        {"review": {"rating": 4}},
    ]

    normalized = normalize_company_data(profile_data, reviews)
    rating = normalized["rating"]

    assert rating["totalReview"] == "3"
    assert rating["overallRating"] == "4.5"
    assert len(normalized["reviews"]) == 3