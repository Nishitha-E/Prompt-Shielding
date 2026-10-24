"""Unit tests for Education Sector PII detection and academic context preservation."""

import pytest
from promptshield.detectors import PIIDetector
from promptshield.redactor import PromptShieldEngine
from promptshield.verhoeff import generate_verhoeff_number


@pytest.fixture
def detector():
    return PIIDetector(seed=42)


def test_detect_student_roll_and_application_no(detector):
    text = "Roll No: 1005-26-749 | Application No: OU26-84920"
    matches = detector.detect_all(text)
    assert len(matches) == 2
    types = [m.pii_type for m in matches]
    assert types == ["STUDENT_ID", "STUDENT_ID"]
    assert matches[0].original == "1005-26-749"
    assert matches[1].original == "OU26-84920"


def test_detect_student_name_header_and_salutation(detector):
    text = "Student Name: Rajesh Sharma\nCourse: M.E. Cyber Security"
    matches = detector.detect_all(text)
    assert len(matches) == 1
    assert matches[0].pii_type == "STUDENT_NAME"
    assert matches[0].original == "Rajesh Sharma"

    text2 = "Bonafide issued to Mr. Suresh Reddy for scholarship verification."
    matches2 = detector.detect_all(text2)
    assert len(matches2) == 1
    assert matches2[0].pii_type == "STUDENT_NAME"
    assert "Suresh Reddy" in matches2[0].original


def test_detect_bank_account_and_pincode(detector):
    text = "Bank A/c No: 38491029481 | Address PIN Code: 500007"
    matches = detector.detect_all(text)
    assert len(matches) == 2
    types = [m.pii_type for m in matches]
    assert "BANK_ACCOUNT" in types
    assert "PINCODE" in types


def test_education_context_preservation():
    """Verify academic qualifications, college names, CGPA, and course queries are NEVER redacted."""
    engine = PromptShieldEngine(seed=42)
    education_text = (
        "--- UNIVERSITY COLLEGE OF ENGINEERING, OSMANIA UNIVERSITY ---\n"
        "Student Name: Rajesh Sharma\n"
        "Roll No: 1005-26-701 | Application No: OU26-49102\n"
        "Course: M.E. Cyber Security (Semester 1)\n"
        "Academic Record: B.Tech CGPA 8.85 / 10.0, GATE Score: 680.\n"
        "Purpose: Applying for ePASS Post-Matric Fee Reimbursement of Rs. 35,000."
    )

    redacted = engine.redact(education_text)

    # Identifiers redacted
    assert "Rajesh Sharma" not in redacted
    assert "1005-26-701" not in redacted
    assert "OU26-49102" not in redacted

    # Academic & Institutional context preserved
    assert "UNIVERSITY COLLEGE OF ENGINEERING, OSMANIA UNIVERSITY" in redacted
    assert "M.E. Cyber Security" in redacted
    assert "B.Tech CGPA 8.85" in redacted
    assert "GATE Score: 680" in redacted
    assert "Post-Matric Fee Reimbursement of Rs. 35,000" in redacted

    # Round trip restore
    restored = engine.restore(redacted)
    assert restored == education_text
