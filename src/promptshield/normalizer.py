import re

def normalize_clinical_text(text: str) -> str:
    if not text:
        return ""

    normalized = text
    normalized = normalized.replace("\u00ad", "").replace("\u200b", "")
    normalized = re.sub(r"([A-Za-z0-9]+-)\r?\n\s*([A-Za-z0-9]+)", r"\1\2", normalized)
    normalized = re.sub(r"(\b\d{4}\s+\d{4})\r?\n\s*(\d{4}\b)", r"\1 \2", normalized)
    normalized = re.sub(r"(\+91)\r?\n\s*([6-9]\d{9}\b)", r"\1 \2", normalized)
    normalized = re.sub(r"([a-zA-Z0-9._%+-]+)\r?\n\s*(@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", r"\1\2", normalized)

    return normalized
