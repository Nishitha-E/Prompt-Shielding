"""Upstream text normalizer for repairing OCR line breaks and formatting anomalies."""

import re


def normalize_clinical_text(text: str) -> str:
    """Repairs split tokens, OCR line breaks, and whitespace anomalies in clinical text."""
    if not text:
        return ""

    normalized = text

    # 1. Remove soft hyphens (\u00ad) and zero-width spaces (\u200b)
    normalized = normalized.replace("\u00ad", "").replace("\u200b", "")

    # 2. Repair line breaks within hyphenated identifiers (e.g. "14-8291-\n0391-4921" or "MRN-\n49210")
    normalized = re.sub(r"([A-Za-z0-9]+-)\r?\n\s*([A-Za-z0-9]+)", r"\1\2", normalized)

    # 3. Repair line breaks within spaced 4-digit numeric chunks (e.g. "2363 5412\n8915" -> "2363 5412 8915")
    normalized = re.sub(r"(\b\d{4}\s+\d{4})\r?\n\s*(\d{4}\b)", r"\1 \2", normalized)

    # 4. Repair line breaks within phone numbers (e.g. "+91\n9876543210" -> "+91 9876543210")
    normalized = re.sub(r"(\+91)\r?\n\s*([6-9]\d{9}\b)", r"\1 \2", normalized)

    # 5. Repair broken email addresses (e.g. "user.name\n@gmail.com" -> "user.name@gmail.com")
    normalized = re.sub(r"([a-zA-Z0-9._%+-]+)\r?\n\s*(@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", r"\1\2", normalized)

    return normalized
