"""Unit tests for clinical text normalizer and OCR artifact healing."""

import pytest
from promptshield.normalizer import normalize_clinical_text
from promptshield.redactor import PromptShieldEngine
from promptshield.verhoeff import generate_verhoeff_number


def test_repair_soft_hyphens():
    text = "Pa\u00adtient Na\u00adme: Mr. Ra\u00adjesh Gupta"
    normalized = normalize_clinical_text(text)
    assert "\u00ad" not in normalized
    assert "Patient Name: Mr. Rajesh Gupta" == normalized


def test_repair_broken_abha_id():
    broken_abha = "ABHA ID: 14-8291-\n0391-4921 registered under ABDM."
    normalized = normalize_clinical_text(broken_abha)
    assert "14-8291-0391-4921" in normalized


def test_repair_broken_aadhaar():
    valid_base = "23635412891"
    full_aadhaar = generate_verhoeff_number(valid_base)
    # Simulate OCR break between 2nd chunk and 3rd chunk
    broken_aadhaar = f"Aadhaar: {full_aadhaar[:4]} {full_aadhaar[4:8]}\n{full_aadhaar[8:]}"
    normalized = normalize_clinical_text(broken_aadhaar)
    expected = f"{full_aadhaar[:4]} {full_aadhaar[4:8]} {full_aadhaar[8:]}"
    assert expected in normalized


def test_repair_broken_phone_and_email():
    broken_text = "Call +91\n9876543210 or email test.doctor\n@hospital.org"
    normalized = normalize_clinical_text(broken_text)
    assert "+91 9876543210" in normalized
    assert "test.doctor@hospital.org" in normalized


def test_end_to_end_redaction_with_ocr_broken_text():
    valid_base = "23635412891"
    full_aadhaar = generate_verhoeff_number(valid_base)
    broken_report = (
        "Student Name: Mr. Ramesh Verma\n"
        f"Aadhaar: {full_aadhaar[:4]} {full_aadhaar[4:8]}\n{full_aadhaar[8:]}\n"
        "Roll No: 1005-26-\n749\n"
        "Course: M.E. Cyber Security."
    )
    engine = PromptShieldEngine(seed=42)
    redacted = engine.redact(broken_report)

    # Identifiers should be detected and redacted despite original OCR line breaks
    assert "Ramesh Verma" not in redacted
    assert full_aadhaar[:4] not in redacted
    assert "1005-26-749" not in redacted
    assert "M.E. Cyber Security" in redacted
