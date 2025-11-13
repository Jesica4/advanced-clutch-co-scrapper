import argparse
import json
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Ensure src/ is on sys.path so namespace packages (parsers, pipelines, utils) are importable
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from clutch_client import ClutchClient
from parsers.company_profile_parser import parse_company_profile
from parsers.reviews_parser import parse_reviews
from pipelines.normalization import normalize_company_data
from pipelines.exporters import export_to_json
from utils.logging_config import setup_logging

def load_settings(path: Optional[Path]) -> Dict[str, Any]:
    if not path:
        return {}
    if not path.exists():
        logging.getLogger(__name__).warning(
            "Settings file %s not found, using defaults.", path
        )
        return {}

    with path.open("r", encoding="utf-8") as f:
        try:
            settings = json.load(f)
        except json.JSONDecodeError as e:
            logging.getLogger(__name__).error(
                "Failed to parse settings file %s: %s", path, e
            )
            return {}
    return settings

def load_input_urls(path: Path) -> List[str]:
    if not path.exists():
        raise FileNotFoundError(f"Input URLs file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        return [str(u) for u in data]

    if isinstance(data, dict):
        if "profile_urls" in data and isinstance(data["profile_urls"], list):
            return [str(u) for u in data["profile_urls"]]
        if "urls" in data and isinstance(data["urls"], list):
            return [str(u) for u in data["urls"]]

    raise ValueError(
        "Unsupported input format. Expected a list of URLs or an object with "
        '"profile_urls"/"urls" key.'
    )

def process_url(
    client: ClutchClient,
    url: str,
) -> Optional[Dict[str, Any]]:
    logger = logging.getLogger(__name__)
    try:
        html = client.fetch_profile(url)
        if not html:
            logger.warning("Empty HTML for URL: %s", url)
            return None

        profile_data = parse_company_profile(html, url)
        reviews = parse_reviews(html)
        normalized = normalize_company_data(profile_data, reviews)
        return normalized
    except Exception as e:  # noqa: BLE001
        logger.exception("Failed to process %s: %s", url, e)
        return None

def run(
    input_path: Path,
    output_path: Path,
    settings_path: Optional[Path],
    logging_config_path: Optional[Path],
) -> None:
    setup_logging(logging_config_path)
    logger = logging.getLogger(__name__)

    settings = load_settings(settings_path)
    logger.debug("Loaded settings: %s", settings)

    urls = load_input_urls(input_path)
    if not urls:
        logger.warning("No URLs found in input file: %s", input_path)
        return

    logger.info("Starting scrape for %d URLs", len(urls))

    client = ClutchClient(
        timeout=float(settings.get("timeout", 15.0)),
        max_retries=int(settings.get("max_retries", 3)),
        user_agent=settings.get(
            "user_agent",
            "AdvancedClutchScraper/1.0 (+https://bitbash.dev)",
        ),
    )

    results: List[Dict[str, Any]] = []
    for url in urls:
        logger.info("Processing %s", url)
        record = process_url(client, url)
        if record is not None:
            results.append(record)

    if not results:
        logger.warning("No records processed successfully; nothing to export.")
        return

    export_to_json(results, output_path)
    logger.info("Exported %d records to %s", len(results), output_path)

def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    root = Path(__file__).resolve().parents[1]
    default_input = root / "data" / "input_urls.sample.json"
    default_output = root / "data" / "sample_output.json"
    default_settings = root / "config" / "settings.example.json"
    default_logging = root / "config" / "logging.example.yaml"

    parser = argparse.ArgumentParser(
        description="Advanced Clutch.co Scrapper - scrape Clutch profiles into JSON."
    )
    parser.add_argument(
        "--input",
        "-i",
        type=Path,
        default=default_input,
        help=f"Path to input JSON with profile URLs (default: {default_input})",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=default_output,
        help=f"Path to output JSON file (default: {default_output})",
    )
    parser.add_argument(
        "--settings",
        "-s",
        type=Path,
        default=default_settings,
        help="Path to settings JSON (timeouts, retries, etc.).",
    )
    parser.add_argument(
        "--logging-config",
        "-l",
        type=Path,
        default=default_logging,
        help="Path to logging YAML config.",
    )

    return parser.parse_args(argv)

if __name__ == "__main__":
    args = parse_args()
    run(
        input_path=args.input,
        output_path=args.output,
        settings_path=args.settings,
        logging_config_path=args.logging_config,
    )