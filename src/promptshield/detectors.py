"""Detectors and format-valid surrogate generators for Indian PII & Healthcare Clinical data."""

import re
import random
import string
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
from promptshield.verhoeff import validate_verhoeff, generate_verhoeff_number


@dataclass
class PIIMatch:
    pii_type: str
    original: str
    start: int
    end: int


class PIIDetector:
    """Detects Indian PII and Healthcare Clinical identifiers, and generates format-valid realistic surrogates."""

    # General Indian Identifiers
    AADHAAR_PATTERN = re.compile(r"\b[2-9]\d{3}[\s-]?[0-9]{4}[\s-]?[0-9]{4}\b")
    PAN_PATTERN = re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b")
    UPI_PATTERN = re.compile(
        r"\b[a-zA-Z0-9._-]+@(okhdfcbank|okaxis|oksbi|icici|ybl|paytm|upi|axl|ibl)\b",
        re.IGNORECASE,
    )
    MOBILE_PATTERN = re.compile(r"\b(?:\+91[\s-]?)?[6-9]\d{9}\b")
    IFSC_PATTERN = re.compile(r"\b[A-Z]{4}0[A-Z0-9]{6}\b")
    EMAIL_PATTERN = re.compile(
        r"\b[a-zA-Z0-9._%+-]+@(?!okhdfcbank|okaxis|oksbi|icici|ybl|paytm|upi|axl|ibl|abdm)[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b",
        re.IGNORECASE,
    )

    # Healthcare / Clinical Identifiers
    ABHA_NUMBER_PATTERN = re.compile(r"\b[1-9]\d{1}-\d{4}-\d{4}-\d{4}\b")
    ABHA_ADDRESS_PATTERN = re.compile(r"\b[a-zA-Z0-9._-]+@abdm\b", re.IGNORECASE)
    PATIENT_ID_PATTERN = re.compile(
        r"\b(?:UHID|MRN|Patient\s*ID|PID|IPD\s*No|OPD\s*No|Reg\s*No)[\s.:#-]+([A-Za-z0-9/-]{4,15})\b",
        re.IGNORECASE,
    )
    PATIENT_HEADER_PATTERN = re.compile(
        r"(?:Patient(?:\s*Name)?|Pt(?:\s*Name)?|Name of Patient)\s*[:\-]\s*([A-Za-z.\s]{3,35})(?=(?:\s{2,}|\n|,|\s+(?:Age|Sex|DOB|Gender|UHID|MRN|IPD|OPD)|$))",
        re.IGNORECASE,
    )
    SALUTATION_NAME_PATTERN = re.compile(
        r"\b(?:Mr\.|Mrs\.|Ms\.|Shri|Smt\.|Master|Baby\s*of)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b"
    )
    DOCTOR_PATTERN = re.compile(
        r"\b(?:Dr\.|Doctor|Dr)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b"
    )
    CONSULTANT_HEADER_PATTERN = re.compile(
        r"(?:Consultant|Treating\s*Doctor|Physician)\s*[:\-]\s*([A-Za-z.\s]{3,35})(?=(?:\s{2,}|\n|,|$))",
        re.IGNORECASE,
    )
    DOB_PATTERN = re.compile(
        r"\b(?:DOB|Date of Birth)[\s.:\-]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b",
        re.IGNORECASE,
    )

    # Synthetic Pools for Healthcare
    FIRST_NAMES = [
        "Aarav", "Rohan", "Aditya", "Vikram", "Suresh", "Kavita", "Ananya", "Pooja",
        "Sunita", "Deepak", "Rajesh", "Priya", "Neha", "Manoj", "Sanjay", "Meera"
    ]
    LAST_NAMES = [
        "Sharma", "Patel", "Verma", "Reddy", "Nair", "Rao", "Gupta", "Kulkarni",
        "Joshi", "Mehta", "Bose", "Chatterjee", "Mishra", "Deshmukh", "Singhania"
    ]

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

        # 7. ABHA Number & Address
        for m in self.ABHA_NUMBER_PATTERN.finditer(text):
            val = m.group(0)
            matches.append(PIIMatch("ABHA", val, m.start(), m.end()))
        for m in self.ABHA_ADDRESS_PATTERN.finditer(text):
            val = m.group(0)
            matches.append(PIIMatch("ABHA", val, m.start(), m.end()))

        # 8. Patient ID / MRN / UHID
        for m in self.PATIENT_ID_PATTERN.finditer(text):
            val = m.group(1).strip()
            # Capture the identifier value span
            start = m.start(1)
            end = m.end(1)
            matches.append(PIIMatch("PATIENT_ID", val, start, end))

        # 9. Doctor Names
        for m in self.DOCTOR_PATTERN.finditer(text):
            val = m.group(0).strip()
            matches.append(PIIMatch("DOCTOR_NAME", val, m.start(), m.end()))
        for m in self.CONSULTANT_HEADER_PATTERN.finditer(text):
            val = m.group(1).strip()
            if val and len(val) > 2:
                matches.append(PIIMatch("DOCTOR_NAME", val, m.start(1), m.end(1)))

        # 10. Patient Names (Header & Salutations)
        for m in self.PATIENT_HEADER_PATTERN.finditer(text):
            val = m.group(1).strip()
            if val and len(val) > 2:
                matches.append(PIIMatch("PATIENT_NAME", val, m.start(1), m.end(1)))
        for m in self.SALUTATION_NAME_PATTERN.finditer(text):
            val = m.group(0).strip()
            matches.append(PIIMatch("PATIENT_NAME", val, m.start(), m.end()))

        # 11. Date of Birth
        for m in self.DOB_PATTERN.finditer(text):
            val = m.group(1).strip()
            matches.append(PIIMatch("DOB", val, m.start(1), m.end(1)))

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
            prefix = str(self._rng.randint(2, 9))
            middle = "".join(str(self._rng.randint(0, 9)) for _ in range(10))
            surrogate_digits = generate_verhoeff_number(prefix + middle)
            if " " in original:
                return f"{surrogate_digits[:4]} {surrogate_digits[4:8]} {surrogate_digits[8:]}"
            elif "-" in original:
                return f"{surrogate_digits[:4]}-{surrogate_digits[4:8]}-{surrogate_digits[8:]}"
            return surrogate_digits

        elif pii_type == "PAN":
            letters1 = "".join(self._rng.choices(string.ascii_uppercase, k=3))
            entity_type = "P"
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

        # Healthcare Surrogates
        elif pii_type == "ABHA":
            if "@abdm" in original.lower():
                user_id = "".join(str(self._rng.randint(0, 9)) for _ in range(6))
                return f"abha{user_id}@abdm"
            part1 = str(self._rng.randint(10, 99))
            part2 = str(self._rng.randint(1000, 9999))
            part3 = str(self._rng.randint(1000, 9999))
            part4 = str(self._rng.randint(1000, 9999))
            return f"{part1}-{part2}-{part3}-{part4}"

        elif pii_type == "PATIENT_ID":
            prefix = "UHID" if "UHID" in original.upper() else ("MRN" if "MRN" in original.upper() else "PID")
            num = self._rng.randint(100000, 999999)
            return f"{prefix}-{num}"

        elif pii_type == "PATIENT_NAME":
            first = self._rng.choice(self.FIRST_NAMES)
            last = self._rng.choice(self.LAST_NAMES)
            # Preserve prefix if present
            for prefix in ["Mr. ", "Mrs. ", "Ms. ", "Shri ", "Smt. ", "Master ", "Baby of "]:
                if original.startswith(prefix):
                    return f"{prefix}{first} {last}"
            return f"{first} {last}"

        elif pii_type == "DOCTOR_NAME":
            first = self._rng.choice(self.FIRST_NAMES)
            last = self._rng.choice(self.LAST_NAMES)
            if original.startswith("Dr. ") or original.startswith("Dr "):
                return f"Dr. {first} {last}"
            return f"Dr. {last}"

        elif pii_type == "DOB":
            day = self._rng.randint(1, 28)
            month = self._rng.randint(1, 12)
            year = self._rng.randint(1960, 2010)
            sep = "/" if "/" in original else "-"
            return f"{day:02d}{sep}{month:02d}{sep}{year}"

        return f"SURROGATE_{pii_type}"
