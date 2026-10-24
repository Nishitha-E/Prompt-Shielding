import re
import random
import string
from promptshield.verhoeff import validate_verhoeff, generate_verhoeff_number

class PIIMatch:
    def __init__(self, pii_type, original, start, end):
        self.pii_type = pii_type
        self.original = original
        self.start = start
        self.end = end

class PIIDetector:
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
    BANK_ACCOUNT_PATTERN = re.compile(
        r"(?:Bank\s*A/c(?:\s*No)?|Account\s*No|A/c\s*No|SB\s*A/c)[\s.:#-]+([0-9]{9,18})\b",
        re.IGNORECASE,
    )
    PINCODE_PATTERN = re.compile(
        r"(?:PIN(?:\s*Code)?|Postal\s*Code|Pincode)[\s.:#-]+([1-9][0-9]{5})\b",
        re.IGNORECASE,
    )
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

    FIRST_NAMES = [
        "Aarav", "Rohan", "Aditya", "Vikram", "Suresh", "Kavita", "Ananya", "Pooja",
        "Sunita", "Deepak", "Rajesh", "Priya", "Neha", "Manoj", "Sanjay", "Meera",
        "Karthik", "Sneha", "Divya", "Ganesh", "Rahul", "Naveen", "Swati", "Harish"
    ]
    LAST_NAMES = [
        "Sharma", "Patel", "Verma", "Reddy", "Nair", "Rao", "Gupta", "Kulkarni",
        "Joshi", "Mehta", "Bose", "Chatterjee", "Mishra", "Deshmukh", "Singhania", "Iyer"
    ]

    def __init__(self, seed=42):
        self._rng = random.Random(seed)

    def detect_all(self, text):
        matches = []

        for m in self.AADHAAR_PATTERN.finditer(text):
            val = m.group(0)
            digits = "".join(d for d in val if d.isdigit())
            if len(digits) == 12 and validate_verhoeff(digits):
                matches.append(PIIMatch("AADHAAR", val, m.start(), m.end()))

        for m in self.PAN_PATTERN.finditer(text):
            matches.append(PIIMatch("PAN", m.group(0), m.start(), m.end()))

        for m in self.UPI_PATTERN.finditer(text):
            matches.append(PIIMatch("UPI", m.group(0), m.start(), m.end()))

        for m in self.MOBILE_PATTERN.finditer(text):
            matches.append(PIIMatch("MOBILE", m.group(0), m.start(), m.end()))

        for m in self.IFSC_PATTERN.finditer(text):
            matches.append(PIIMatch("IFSC", m.group(0), m.start(), m.end()))

        for m in self.EMAIL_PATTERN.finditer(text):
            matches.append(PIIMatch("EMAIL", m.group(0), m.start(), m.end()))

        for m in self.BANK_ACCOUNT_PATTERN.finditer(text):
            matches.append(PIIMatch("BANK_ACCOUNT", m.group(1).strip(), m.start(1), m.end(1)))

        for m in self.PINCODE_PATTERN.finditer(text):
            matches.append(PIIMatch("PINCODE", m.group(1).strip(), m.start(1), m.end(1)))

        for m in self.STUDENT_ID_PATTERN.finditer(text):
            matches.append(PIIMatch("STUDENT_ID", m.group(1).strip(), m.start(1), m.end(1)))

        for m in self.STUDENT_HEADER_PATTERN.finditer(text):
            val = m.group(1).strip()
            if val and len(val) > 2:
                matches.append(PIIMatch("STUDENT_NAME", val, m.start(1), m.end(1)))

        for m in self.SALUTATION_NAME_PATTERN.finditer(text):
            matches.append(PIIMatch("STUDENT_NAME", m.group(0).strip(), m.start(), m.end()))

        for m in self.DOB_PATTERN.finditer(text):
            matches.append(PIIMatch("DOB", m.group(1).strip(), m.start(1), m.end(1)))

        matches.sort(key=lambda m: (m.start, -(m.end - m.start)))
        filtered = []
        last_end = -1
        for m in matches:
            if m.start >= last_end:
                filtered.append(m)
                last_end = m.end

        return filtered

    def generate_surrogate(self, pii_type, original):
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
            l1 = "".join(self._rng.choices(string.ascii_uppercase, k=3))
            l5 = self._rng.choice(string.ascii_uppercase)
            digits = "".join(str(self._rng.randint(0, 9)) for _ in range(4))
            l_last = self._rng.choice(string.ascii_uppercase)
            return f"{l1}P{l5}{digits}{l_last}"

        elif pii_type == "UPI":
            handle = original.split("@")[-1] if "@" in original else "sbi"
            user = "student" + "".join(str(self._rng.randint(0, 9)) for _ in range(4))
            return f"{user}@{handle}"

        elif pii_type == "MOBILE":
            prefix = "+91 " if original.startswith("+91 ") else ("+91-" if original.startswith("+91-") else ("+91" if original.startswith("+91") else ""))
            first_digit = str(self._rng.randint(6, 9))
            rest = "".join(str(self._rng.randint(0, 9)) for _ in range(9))
            return f"{prefix}{first_digit}{rest}"

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
            for sal in ["Mr. ", "Ms. ", "Shri ", "Smt. ", "Kumar ", "Kumari "]:
                if original.startswith(sal):
                    return f"{sal}{first} {last}"
            return f"{first} {last}"

        elif pii_type == "DOB":
            day = self._rng.randint(1, 28)
            month = self._rng.randint(1, 12)
            year = self._rng.randint(1998, 2006)
            sep = "/" if "/" in original else "-"
            return f"{day:02d}{sep}{month:02d}{sep}{year}"

        return f"SURROGATE_{pii_type}"
