import hashlib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ExtractedContent:
    path: Path
    text: str
    content_hash: str
    content_available: bool
    extraction_version: str


def extract_local_file_content(path: Path) -> ExtractedContent:
    if not path.exists():
        raise FileNotFoundError(path)

    if path.is_dir():
        raise IsADirectoryError(path)

    if path.suffix.lower() not in {".txt"}:
        raise ValueError(f"Unsupported file type: {path.suffix or '<none>'}")

    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"Unable to decode file as UTF-8: {path}") from exc

    content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()

    return ExtractedContent(
        path=path,
        text=text,
        content_hash=content_hash,
        content_available=True,
        extraction_version="1",
    )
