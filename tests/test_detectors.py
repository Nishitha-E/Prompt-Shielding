"""Unit tests for Indian PII detectors and surrogate generators."""

import pytest
from promptshield.detectors import PIIDetector
from promptshield.verhoeff import validate_verhoeff, generate_verhoeff_number


@pytest.fixture
def detector():
    return PIIDetector(seed=12345)


def test_detect_aadhaar(detector):
    valid_aadhaar = generate_verhoeff_number("23635412891")  # 12 digits starting with 2
    formatted_aadhaar = f"{valid_aadhaar[:4]} {valid_aadhaar[4:8]} {valid_aadhaar[8:]}"
    text = f"My Aadhaar number is {formatted_aadhaar}."
    
    matches = detector.detect_all(text)
    assert len(matches) == 1
    assert matches[0].pii_type == "AADHAAR"
    assert matches[0].original == formatted_aadhaar


def test_detect_pan(detector):
    text = "Please check PAN card ABCDE1234F for verification."
    matches = detector.detect_all(text)
    assert len(matches) == 1
    assert matches[0].pii_type == "PAN"
    assert matches[0].original == "ABCDE1234F"


def test_detect_upi(detector):
    text = "Transfer money to rahul@okhdfcbank or priya@ybl."
    matches = detector.detect_all(text)
    assert len(matches) == 2
    types = [m.pii_type for m in matches]
    assert types == ["UPI", "UPI"]


def test_detect_mobile(detector):
    text = "Call me at +91 9876543210 or 8765432109."
    matches = detector.detect_all(text)
    assert len(matches) == 2
    assert all(m.pii_type == "MOBILE" for m in matches)


def test_detect_ifsc(detector):
    text = "Bank branch code is SBIN0001234."
    matches = detector.detect_all(text)
    assert len(matches) == 1
    assert matches[0].pii_type == "IFSC"


def test_detect_email(detector):
    text = "Contact me at user.name@example.com for details."
    matches = detector.detect_all(text)
    assert len(matches) == 1
    assert matches[0].pii_type == "EMAIL"


def test_surrogate_aadhaar_checksum_validity(detector):
    surrogate = detector.generate_surrogate("AADHAAR", "2363 5412 8913")
    digits = "".join(d for d in surrogate if d.isdigit())
    assert len(digits) == 12
    assert validate_verhoeff(digits) is True
