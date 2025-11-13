import sys
from pathlib import Path

import pytest

# Ensure src/ is importable
ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from parsers.company_profile_parser import parse_company_profile
from parsers.reviews_parser import parse_reviews

SAMPLE_HTML = """
<html>
<head>
  <meta property="og:title" content="Example Company" />
  <meta property="og:description" content="Example description." />
  <meta property="og:url" content="https://clutch.co/profile/example-company" />
  <meta property="og:image" content="https://example.com/logo.png" />
</head>
<body>
  <h1>Example Company</h1>
  <div itemtype="http://schema.org/AggregateRating">
    <span itemprop="ratingValue">4.8</span>
    <span itemprop="reviewCount">10</span>
  </div>

  <div itemtype="http://schema.org/PostalAddress">
    <span itemprop="streetAddress">123 Main St</span>
    <span itemprop="addressLocality">Sample City, Country</span>
    <span itemprop="addressRegion">SC</span>
    <span itemprop="addressCountry">XX</span>
    <span itemprop="postalCode">00000</span>
  </div>

  <div itemtype="http://schema.org/Review">
    <span itemprop="name">Great work</span>
    <span itemprop="datePublished">2024-01-01</span>
    <div itemprop="reviewRating">
      <span itemprop="ratingValue">5</span>
    </div>
    <p itemprop="reviewBody">Very happy with the collaboration.</p>
    <span itemprop="author">Jane Doe</span>
  </div>
</body>
</html>
"""

def test_company_profile_parser_basic():
    data = parse_company_profile(SAMPLE_HTML, "https://clutch.co/profile/example-company")
    summary = data["summary"]

    assert summary["name"] == "Example Company"
    assert summary["description"] == "Example description."
    assert summary["rating"] == "4.8"
    assert summary["totalReview"] == "10"

    assert data["profileURL"] == "https://clutch.co/profile/example-company"
    assert isinstance(data["addresses"], list)
    assert len(data["addresses"]) == 1
    addr = data["addresses"][0]
    assert addr["streetAddress"] == "123 Main St"
    assert addr["postalCode"] == "00000"

def test_reviews_parser_schema_org():
    reviews = parse_reviews(SAMPLE_HTML)
    assert len(reviews) == 1
    r = reviews[0]
    assert r["name"] == "Great work"
    assert r["datePublished"] == "2024-01-01"
    assert r["review"]["rating"] == 5.0
    assert "happy with the collaboration" in (r["review"]["review"] or "")
    assert r["reviewer"]["name"] == "Jane Doe"