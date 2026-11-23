"""Manuscript ingestion and provenance parser."""

from typing import Dict, List, Tuple
from packages.schemas.enums import AssetType
from packages.shared.security import sanitize_filename


class ManuscriptParser:
    """Parses raw text, Markdown, scripts, and handles provenance boundaries."""

    def parse_text(self, filename: str, content: str) -> Dict[str, object]:
        safe_name = sanitize_filename(filename)
        cleaned = content.replace("\r\n", "\n")
        paragraphs = [p.strip() for p in cleaned.split("\n\n") if p.strip()]

        char_count = len(cleaned)
        word_count = len(cleaned.split())

        return {
            "original_filename": safe_name,
            "asset_type": AssetType.TEXT,
            "raw_text": cleaned,
            "char_count": char_count,
            "word_count": word_count,
            "paragraph_count": len(paragraphs),
        }
