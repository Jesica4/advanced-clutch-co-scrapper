# Clutch Data Model

This document describes the JSON structure produced by the Advanced Clutch.co Scrapper.

## Top-level Structure

The output is a JSON array. Each element represents a single company profile with the following top-level fields:

- `summary`
- `addresses`
- `verification`
- `chartPie`
- `rating`
- `websiteUrl`
- `profileURL`
- `reviews`
- `reviewInsights`

## `summary`

High-level information about the company:

- `name`: Official company name from the profile.
- `logo`: URL of the company logo image.
- `tagLine`: Short tagline or positioning statement.
- `description`: Long-form description of services and capabilities.
- `totalReview`: Total number of reviews.
- `rating`: Overall rating value.
- `verificationStatus`: Clutch verification badge text, when available.
- `minProjectSize`: Minimum project size (e.g. "$50,000+").
- `averageHourlyRate`: Hourly rate range text.
- `employees`: Employee count band.
- `founded`: Founding year text.
- `video_url`: Embedded video URL, if present.
- `languages`: List of supported languages.
- `timezones`: List of time zones where the team operates.

## `addresses[]`

Each address object describes one office location:

- `title`: Label for the location (e.g. "Headquarters").
- `streetAddress`: Street address.
- `locality`: City and country.
- `region`: Region or state code.
- `country`: ISO country code.
- `postalCode`: Postal or ZIP code.
- `locationEmployees`: Employee band for that office.
- `telephone`: Contact phone number.

## `verification`

Compliance and legal verification information:

- `businessEntity`: Details about the legal entity (name, source, jurisdiction, status, dates, registration ID).
- `paymentLegalFilings`: High-level payment and legal filing flags (bankruptcy, tax liens, etc.).

## `chartPie`

Breakdowns used for charts in BI tools:

- `service_provided.slices[]`: Service line distribution with fields:
  - `name`
  - `percent`
  - `PercentHundreds`
  - `url`
- `focus.charts.*.slices[]`: Focus distributions for technologies, platforms, etc.
- `industries.slices[]`: Industry segments with percentage shares.
- `clients.slices[]`: Client-size segments (enterprise, midmarket, SMB).

## `rating`

Aggregated rating metrics:

- `totalReview`: Total review count.
- `overallRating`: Overall rating value.

These may be recomputed during normalization based on collected reviews.

## `reviews[]`

Each review entry captures feedback for a specific project:

- `name`: Review title.
- `datePublished`: Publication date.
- `project.*`: Project metadata (name, budget band, length, description, categories).
- `review.rating`: Overall project rating (numeric).
- `review.quality`, `review.schedule`, `review.cost`, `review.willingToRefer`: Dimension-specific ratings, when present.
- `review.review`: Short highlight quote.
- `review.comments`: Full narrative review text.
- `reviewer.*`: Reviewer attributes (name, title, industry, company size, location, type, verification).

## `reviewInsights`

Aggregated insights derived from the reviews:

- `topMentions[]`: Frequently appearing phrases (e.g. "High-quality work").
- `reviewHighlights[]`: Curated summary cards of recurring strengths, weaknesses, or themes.

This structure is designed to be directly consumable by BI tools, notebooks, dashboards, and CRMs without additional normalization.