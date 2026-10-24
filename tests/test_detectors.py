from promptshield.detectors import PIIDetector
from promptshield.verhoeff import validate_verhoeff, generate_verhoeff_number

def test_detect_aadhaar():
    d = PIIDetector(seed=42)
    val = generate_verhoeff_number("23635412891")
    formatted = f"{val[:4]} {val[4:8]} {val[8:]}"
    matches = d.detect_all(f"Aadhaar: {formatted}")
    assert len(matches) == 1
    assert matches[0].pii_type == "AADHAAR"
    assert matches[0].original == formatted

def test_detect_pan():
    d = PIIDetector(seed=42)
    matches = d.detect_all("PAN card is ABCDE1234F.")
    assert len(matches) == 1
    assert matches[0].pii_type == "PAN"
    assert matches[0].original == "ABCDE1234F"

def test_detect_upi():
    d = PIIDetector(seed=42)
    matches = d.detect_all("Pay to student@oksbi or rahul@ybl")
    assert len(matches) == 2
    assert [m.pii_type for m in matches] == ["UPI", "UPI"]

def test_detect_mobile():
    d = PIIDetector(seed=42)
    matches = d.detect_all("Contact: +91 9876543210 or 8765432109")
    assert len(matches) == 2
    assert all(m.pii_type == "MOBILE" for m in matches)

def test_detect_ifsc():
    d = PIIDetector(seed=42)
    matches = d.detect_all("IFSC code is SBIN0001234")
    assert len(matches) == 1
    assert matches[0].pii_type == "IFSC"

def test_detect_email():
    d = PIIDetector(seed=42)
    matches = d.detect_all("Email: user@example.com")
    assert len(matches) == 1
    assert matches[0].pii_type == "EMAIL"

def test_detect_student_id_and_name():
    d = PIIDetector(seed=42)
    text = "Student Name: Rajesh Sharma\nRoll No: 1005-26-701"
    matches = d.detect_all(text)
    types = [m.pii_type for m in matches]
    assert "STUDENT_NAME" in types
    assert "STUDENT_ID" in types

def test_detect_bank_and_pincode():
    d = PIIDetector(seed=42)
    text = "Bank A/c No: 38491029481, Address PIN Code: 500007"
    matches = d.detect_all(text)
    types = [m.pii_type for m in matches]
    assert "BANK_ACCOUNT" in types
    assert "PINCODE" in types

def test_surrogate_aadhaar_validity():
    d = PIIDetector(seed=42)
    surrogate = d.generate_surrogate("AADHAAR", "2363 5412 8913")
    digits = "".join(ch for ch in surrogate if ch.isdigit())
    assert len(digits) == 12
    assert validate_verhoeff(digits) is True
