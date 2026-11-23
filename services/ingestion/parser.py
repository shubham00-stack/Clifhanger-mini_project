"""Manuscript ingestion and provenance parser supporting PDF, DOCX, and TXT."""

import io
import os
import re
from typing import Dict, List, Optional
from pypdf import PdfReader
from docx import Document
from packages.schemas.enums import AssetType
from packages.shared.security import sanitize_filename
from packages.shared.errors import IngestionError


class ManuscriptParser:
    """Parses raw text, PDF, DOCX, scripts, and handles provenance boundaries."""

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
            "page_count": max(1, word_count // 250),
        }

    def parse_pdf(self, filename: str, file_bytes: bytes) -> Dict[str, object]:
        """Extracts text, page numbers, and provenance metadata from PDF documents."""
        if not file_bytes:
            raise IngestionError(f"PDF document '{filename}' is empty (0 bytes).")

        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            safe_name = sanitize_filename(filename)
            pages_data = []
            full_text_parts = []

            if reader.is_encrypted:
                try:
                    reader.decrypt("")
                except Exception as dec_err:
                    raise IngestionError(f"PDF document '{filename}' is encrypted and password was not provided.") from dec_err

            for page_idx, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                cleaned_text = re.sub(r"\r\n|\r", "\n", page_text).strip()
                pages_data.append({
                    "page_number": page_idx + 1,
                    "text": cleaned_text,
                    "char_count": len(cleaned_text),
                })
                if cleaned_text:
                    full_text_parts.append(cleaned_text)

            full_text = "\n\n".join(full_text_parts)
            return {
                "original_filename": safe_name,
                "asset_type": AssetType.PDF,
                "raw_text": full_text,
                "char_count": len(full_text),
                "word_count": len(full_text.split()),
                "page_count": len(reader.pages),
                "pages": pages_data,
            }
        except IngestionError:
            raise
        except Exception as e:
            raise IngestionError(f"Failed to parse PDF document {filename}: {str(e)}") from e

    def parse_docx(self, filename: str, file_bytes: bytes) -> Dict[str, object]:
        """Extracts paragraphs and styles from Microsoft Word DOCX manuscripts."""
        if not file_bytes:
            raise IngestionError(f"DOCX document '{filename}' is empty (0 bytes).")

        try:
            doc = Document(io.BytesIO(file_bytes))
            safe_name = sanitize_filename(filename)
            paragraphs_data = []
            full_text_parts = []

            for p_idx, para in enumerate(doc.paragraphs):
                text = para.text.strip()
                if not text:
                    continue
                paragraphs_data.append({
                    "paragraph_index": p_idx + 1,
                    "style": para.style.name if para.style else "Normal",
                    "text": text,
                })
                full_text_parts.append(text)

            full_text = "\n\n".join(full_text_parts)
            return {
                "original_filename": safe_name,
                "asset_type": AssetType.DOCX,
                "raw_text": full_text,
                "char_count": len(full_text),
                "word_count": len(full_text.split()),
                "paragraph_count": len(paragraphs_data),
                "paragraphs": paragraphs_data,
                "page_count": max(1, len(full_text.split()) // 250),
            }
        except IngestionError:
            raise
        except Exception as e:
            raise IngestionError(f"Failed to parse DOCX document {filename}: {str(e)}") from e

    def parse_file(self, filename: str, file_bytes: bytes) -> Dict[str, object]:
        """Universal parser routing to PDF, DOCX, or text parser."""
        ext = os.path.splitext(filename)[1].lower()
        if ext == ".pdf":
            return self.parse_pdf(filename, file_bytes)
        elif ext in [".docx", ".doc"]:
            return self.parse_docx(filename, file_bytes)
        else:
            text_content = file_bytes.decode("utf-8", errors="replace")
            return self.parse_text(filename, text_content)
