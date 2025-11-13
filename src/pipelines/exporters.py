from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Iterable, Union

logger = logging.getLogger(__name__)

def export_to_json(
    records: Iterable[dict],
    output_path: Union[str, Path],
) -> None:
    """Export a sequence of normalized records into a JSON file."""
    path = Path(output_path)
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)

    data = list(records)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info("Wrote %d records to %s", len(data), path)