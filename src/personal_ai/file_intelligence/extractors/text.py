"""Plain-text file extractor."""

from __future__ import annotations

import hashlib
from pathlib import Path

from personal_ai.file_intelligence.extractors.registry import (
    ExtractedContent,
)


class TextFileExtractor:
    """Extract UTF-8 text from one explicitly selected .txt file."""

    extractor_type = "text"

    def extract(self, source_path: str) -> ExtractedContent:
        path = Path(source_path).expanduser().resolve()

        if not path.exists():
            raise FileNotFoundError(path)

        if path.is_dir():
            raise IsADirectoryError(path)

        if path.suffix.casefold() != ".txt":
            raise ValueError(
                f"Unsupported file type: {path.suffix or '<none>'}"
            )

        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(
                f"Unable to decode file as UTF-8: {path}"
            ) from exc

        content_hash = hashlib.sha256(
            text.encode("utf-8")
        ).hexdigest()

        return ExtractedContent(
            source_path=str(path),
            text=text,
            content_hash=content_hash,
            extraction_format="text",
            extraction_version="1",
        )
