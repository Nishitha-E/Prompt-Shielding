"""Detectors and format-valid surrogate generators for Indian PII in the Education Sector."""

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
    """Detects Indian statutory identifiers and student personal data in education prompts,

    generating format-valid realistic synthetic surrogates.
    """

    # 1. Statutory National & Financial Identifiers
    AADHAAR_PATTERN = re.compile(r"\b[2-9]\d{3}[\s-]?[0-9]{4}[\s-]?[0-9]{4}\b")
    PAN_PATTERN = re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b")
    UPI_PATTERN = re.compile(
        r"\b[a-zA-Z0-9._-]+@(okhdfcbank|okaxis|oksbi|icici|ybl|paytm|upi|axl|ibl|sbi)\b",
        re.IGNORECASE,
    )
    MOBILE_PATTERN = re.compile(r"\b(?:\+91[\s-]?)?[6-9]\d{9}\b")
    IFSC_PATTERN = re.compile(r"\b[A-Z]{4}0[A-Z0-9]{6}\b")
    EMAIL_PATTERN = re.compile(
        r"\b[a-zA-Z0-9._%+-]+@(?!okhdfcbank|okaxis|oksbi|icici|ybl|paytm|upi|axl|ibl)[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b",
        re.IGNORECASE,
    )

    # 2. Bank Account Numbers (anchored to banking context)
    BANK_ACCOUNT_PATTERN = re.compile(
        r"(?:Bank\s*A/c(?:\s*No)?|Account\s*No|A/c\s*No|SB\s*A/c)[\s.:#-]+([0-9]{9,18})\b",
        re.IGNORECASE,
    )

    # 3. Indian Postal PIN Codes (anchored to Address/PIN context)
    PINCODE_PATTERN = re.compile(
        r"(?:PIN(?:\s*Code)?|Postal\s*Code|Pincode)[\s.:#-]+([1-9][0-9]{5})\b",
        re.IGNORECASE,
    )

    # 4. Education & Student Identifiers
    STUDENT_ID_PATTERN = re.compile(
        r"\b(?:Roll\s*No|Application\s*No|App\s*No|Hall\s*Ticket\s*No|HT\s*No|Enrollment\s*No|Reg(?:istration)?\s*No|Student\s*ID)[\s.:#-]+([A-Za-z0-9/-]{5,20})\b",
        re.IGNORECASE,
    )
    STUDENT_HEADER_PATTERN = re.compile(
        r"(?:Student(?:\s*Name)?|Candidate(?:\s*Name)?|Applicant(?:\s*Name)?|Name of Student)\s*[:\-]\s*([A-Za-z. ]{3,35})(?=(?:\s{2,}|\r?\n|,|$))",
        re.IGNORECASE,
    )
    SALUTATION_NAME_PATTERN = re.compile(
        r"\b(?:Mr\.|Ms\.|Shri|Smt\.|Kumar|Kumari)[ \t]+([A-Z][a-z]+(?:[ \t]+[A-Z][a-z]+){1,3})\b"
    )
    DOB_PATTERN = re.compile(
        r"\b(?:DOB|Date of Birth)[\s.:\-]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b",
        re.IGNORECASE,
    )

    # Synthetic Indian Names (modeled after Indic Synthetic Profiles)
    FIRST_NAMES = [
        "Aarav", "Rohan", "Aditya", "Vikram", "Suresh", "Kavita", "Ananya", "Pooja",
        "Sunita", "Deepak", "Rajesh", "Priya", "Neha", "Manoj", "Sanjay", "Meera",
        "Karthik", "Sneha", "Divya", "Ganesh", "Rahul", "Naveen", "Swati", "Harish"
    ]
    LAST_NAMES = [
        "Sharma", "Patel", "Verma", "Reddy", "Nair", "Rao", "Gupta", "Kulkarni",
        "Joshi", "Mehta", "Bose", "Chatterjee", "Mishra", "Deshmukh", "Singhania", "Iyer"
    ]

    def __init__(self, seed: int = 42):
        self._rng = random.Random(seed)

    def detect_all(self, text: str) -> List[PIIMatch]:
        """Detect all non-overlapping PII occurrences in education prompts."""
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

        # 7. Bank Account Number
        for m in self.BANK_ACCOUNT_PATTERN.finditer(text):
            val = m.group(1).strip()
            matches.append(PIIMatch("BANK_ACCOUNT", val, m.start(1), m.end(1)))

        # 8. Postal PIN Code
        for m in self.PINCODE_PATTERN.finditer(text):
            val = m.group(1).strip()
            matches.append(PIIMatch("PINCODE", val, m.start(1), m.end(1)))

        # 9. Student / Applicant ID
        for m in self.STUDENT_ID_PATTERN.finditer(text):
            val = m.group(1).strip()
            matches.append(PIIMatch("STUDENT_ID", val, m.start(1), m.end(1)))

        # 10. Student Names (Headers & Salutations)
        for m in self.STUDENT_HEADER_PATTERN.finditer(text):
            val = m.group(1).strip()
            if val and len(val) > 2:
                matches.append(PIIMatch("STUDENT_NAME", val, m.start(1), m.end(1)))
        for m in self.SALUTATION_NAME_PATTERN.finditer(text):
            val = m.group(0).strip()
            matches.append(PIIMatch("STUDENT_NAME", val, m.start(), m.end()))

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
        """Generate a realistic, format-valid surrogate for the given identifier."""
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
            entity_type = "P"  # Individual Person
            letter5 = self._rng.choice(string.ascii_uppercase)
            digits = "".join(str(self._rng.randint(0, 9)) for _ in range(4))
            last_letter = self._rng.choice(string.ascii_uppercase)
            return f"{letters1}{entity_type}{letter5}{digits}{last_letter}"

        elif pii_type == "UPI":
            handle = original.split("@")[-1] if "@" in original else "sbi"
            user_part = "student" + "".join(str(self._rng.randint(0, 9)) for _ in range(4))
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
            domain = original.split("@")[-1] if "@" in original else "gmail.com"
            uname = "student" + "".join(str(self._rng.randint(0, 9)) for _ in range(5))
            return f"{uname}@{domain}"

        elif pii_type == "BANK_ACCOUNT":
            length = len(original) if len(original) >= 9 else 12
            return "".join(str(self._rng.randint(0, 9)) for _ in range(length))

        elif pii_type == "PINCODE":
            # Realistic Indian 6-digit postal code
            first = self._rng.randint(1, 8)
            rest = "".join(str(self._rng.randint(0, 9)) for _ in range(5))
            return f"{first}{rest}"

        elif pii_type == "STUDENT_ID":
            prefix = "OU" if "OU" in original.upper() else ("APP" if "APP" in original.upper() else "REG")
            num = self._rng.randint(100000, 999999)
            return f"{prefix}-{num}"

        elif pii_type == "STUDENT_NAME":
            first = self._rng.choice(self.FIRST_NAMES)
            last = self._rng.choice(self.LAST_NAMES)
            for prefix in ["Mr. ", "Ms. ", "Shri ", "Smt. ", "Kumar ", "Kumari "]:
                if original.startswith(prefix):
                    return f"{prefix}{first} {last}"
            return f"{first} {last}"

        elif pii_type == "DOB":
            day = self._rng.randint(1, 28)
            month = self._rng.randint(1, 12)
            year = self._rng.randint(1998, 2006)
            sep = "/" if "/" in original else "-"
            return f"{day:02d}{sep}{month:02d}{sep}{year}"

        return f"SURROGATE_{pii_type}"
