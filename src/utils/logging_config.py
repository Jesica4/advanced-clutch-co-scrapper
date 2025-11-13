from __future__ import annotations

import logging
import logging.config
from pathlib import Path
from typing import Optional

import yaml

def setup_logging(config_path: Optional[Path] = None) -> None:
    """Configure logging from YAML if available, otherwise use basicConfig."""
    if config_path and config_path.exists():
        with config_path.open("r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        )