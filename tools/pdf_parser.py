import io
import re
from typing import Dict, Tuple, Any
from pypdf import PdfReader


def clean_text(text: str) -> str:
    """Normalize whitespace, remove null characters and line artifacts."""
    if not text:
        return ""
    # Remove null bytes
    text = text.replace("\x00", "")
    # Normalize multiple whitespace/newlines
    text = re.sub(r"\r\n|\r", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def parse_pdf_text(pdf_bytes: bytes) -> Tuple[str, Dict[str, Any]]:
    """
    Extract raw text and detect major sections (Abstract, Introduction, Method, Conclusion, etc.)
    from PDF bytes.
    """
    reader = PdfReader(io.BytesIO(pdf_bytes))
    page_texts = []
    
    for i, page in enumerate(reader.pages):
        try:
            page_str = page.extract_text() or ""
            page_texts.append(page_str)
        except Exception:
            continue

    raw_text = clean_text("\n\n".join(page_texts))
    
    # Heuristic section detection
    section_patterns = {
        "abstract": r"(?i)(?:^|\n)\s*(?:abstract)\s*[:.\n]\s*(.*?)(?=\n\s*(?:1\.?|I\.?|introduction)|\Z)",
        "introduction": r"(?i)(?:^|\n)\s*(?:1\.?|I\.?)\s*(?:introduction)\s*[:.\n]\s*(.*?)(?=\n\s*(?:2\.?|II\.?|\d\.)|\Z)",
        "method": r"(?i)(?:^|\n)\s*(?:\d\.?|[IVX]+\.?)\s*(?:method|methodology|model|approach|architecture|proposed)\s*[:.\n]\s*(.*?)(?=\n\s*(?:\d\.?|[IVX]+\.?)\s*(?:experiments|results|discussion|conclusion|references)|\Z)",
        "conclusion": r"(?i)(?:^|\n)\s*(?:\d\.?|[IVX]+\.?)\s*(?:conclusion|discussion|summary)\s*[:.\n]\s*(.*?)(?=\n\s*(?:references|acknowledgments|bibliography)|\Z)",
    }

    sections: Dict[str, Any] = {
        "full_text": raw_text,
        "page_count": len(reader.pages),
    }

    for sec_name, pattern in section_patterns.items():
        match = re.search(pattern, raw_text, re.DOTALL)
        if match:
            extracted = clean_text(match.group(1))
            if len(extracted) > 40:  # Valid content check
                sections[sec_name] = extracted

    # If method not explicitly captured by regex, take the core body (pages 1 to 5 or first 12,000 chars)
    if "method" not in sections:
        core_preview = raw_text[:12000]
        sections["core_preview"] = core_preview

    return raw_text, sections

