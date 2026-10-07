"""Detectors and format-valid surrogate generators for Indian PII types."""

import re
import random
import string
from dataclasses import dataclass
from typing import List, Tuple, Dict
from promptshield.verhoeff import validate_verhoeff, generate_verhoeff_number


@dataclass
class PIIMatch:
    pii_type: str
    original: str
    start: int
    end: int


class PIIDetector:
    """Detects Indian PII and generates format-valid realistic surrogates."""

    AADHAAR_PATTERN = re.compile(r"\b[2-9]\d{3}[\s-]?[0-9]{4}[\s-]?[0-9]{4}\b")
    PAN_PATTERN = re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b")
    UPI_PATTERN = re.compile(
        r"\b[a-zA-Z0-9._-]+@(okhdfcbank|okaxis|oksbi|icici|ybl|paytm|upi|axl|ibl)\b",
        re.IGNORECASE,
    )
    MOBILE_PATTERN = re.compile(r"\b(?:\+91[\s-]?)?[6-9]\d{9}\b")
    IFSC_PATTERN = re.compile(r"\b[A-Z]{4}0[A-Z0-9]{6}\b")
    EMAIL_PATTERN = re.compile(
        r"\b[a-zA-Z0-9._%+-]+@(?!okhdfcbank|okaxis|oksbi|icici|ybl|paytm|upi|axl|ibl)[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b",
        re.IGNORECASE,
    )

    def __init__(self, seed: int = 42):
        self._rng = random.Random(seed)

    def detect_all(self, text: str) -> List[PIIMatch]:
        """Detect all non-overlapping PII occurrences in text."""
        matches: List[PIIMatch] = []

        # 1. Aadhaar
        for m in self.AADHAAR_PATTERN.finditer(text):
            val = m.group(0)
            digits_only = "".join(d for d in val if d.isdigit())
            if len(digits_only) == 12 and validate_verhoeff(digits_only):
                matches.append(PIIMatch("AADHAAR", val, m.start(), m.end()))

        # 2. PAN
        for m in self.PAN_PATTERN.finditer(text):
            val = m.group(0)
            matches.append(PIIMatch("PAN", val, m.start(), m.end()))

        # 3. UPI VPA
        for m in self.UPI_PATTERN.finditer(text):
            val = m.group(0)
            matches.append(PIIMatch("UPI", val, m.start(), m.end()))

        # 4. Mobile
        for m in self.MOBILE_PATTERN.finditer(text):
            val = m.group(0)
            matches.append(PIIMatch("MOBILE", val, m.start(), m.end()))

        # 5. IFSC
        for m in self.IFSC_PATTERN.finditer(text):
            val = m.group(0)
            matches.append(PIIMatch("IFSC", val, m.start(), m.end()))

        # 6. Email
        for m in self.EMAIL_PATTERN.finditer(text):
            val = m.group(0)
            matches.append(PIIMatch("EMAIL", val, m.start(), m.end()))

        # Remove overlapping matches (prefer longer/earlier matches)
        matches.sort(key=lambda m: (m.start, -(m.end - m.start)))
        filtered: List[PIIMatch] = []
        last_end = -1
        for m in matches:
            if m.start >= last_end:
                filtered.append(m)
                last_end = m.end

        return filtered

    def generate_surrogate(self, pii_type: str, original: str) -> str:
        """Generate a realistic, format-valid surrogate for the given PII type."""
        if pii_type == "AADHAAR":
            # Generate 11 random digits starting with 2-9, append Verhoeff check digit
            prefix = str(self._rng.randint(2, 9))
            middle = "".join(str(self._rng.randint(0, 9)) for _ in range(10))
            surrogate_digits = generate_verhoeff_number(prefix + middle)
            # Preserve spacing/dashing format of original
            if " " in original:
                return f"{surrogate_digits[:4]} {surrogate_digits[4:8]} {surrogate_digits[8:]}"
            elif "-" in original:
                return f"{surrogate_digits[:4]}-{surrogate_digits[4:8]}-{surrogate_digits[8:]}"
            return surrogate_digits

        elif pii_type == "PAN":
            letters1 = "".join(self._rng.choices(string.ascii_uppercase, k=3))
            entity_type = "P"  # Individual Person
            letter5 = self._rng.choice(string.ascii_uppercase)
            digits = "".join(str(self._rng.randint(0, 9)) for _ in range(4))
            last_letter = self._rng.choice(string.ascii_uppercase)
            return f"{letters1}{entity_type}{letter5}{digits}{last_letter}"

        elif pii_type == "UPI":
            handle = original.split("@")[-1] if "@" in original else "upi"
            user_part = "user" + "".join(str(self._rng.randint(0, 9)) for _ in range(4))
            return f"{user_part}@{handle}"

        elif pii_type == "MOBILE":
            prefix_char = "+91 " if original.startswith("+91 ") else ("+91-" if original.startswith("+91-") else ("+91" if original.startswith("+91") else ""))
            first_digit = str(self._rng.randint(6, 9))
            rest_digits = "".join(str(self._rng.randint(0, 9)) for _ in range(9))
            return f"{prefix_char}{first_digit}{rest_digits}"

        elif pii_type == "IFSC":
            bank = "".join(self._rng.choices(string.ascii_uppercase, k=4))
            branch = "".join(self._rng.choices(string.ascii_uppercase + string.digits, k=6))
            return f"{bank}0{branch}"

        elif pii_type == "EMAIL":
            domain = original.split("@")[-1] if "@" in original else "example.com"
            uname = "anon" + "".join(str(self._rng.randint(0, 9)) for _ in range(5))
            return f"{uname}@{domain}"

        return f"SURROGATE_{pii_type}"
