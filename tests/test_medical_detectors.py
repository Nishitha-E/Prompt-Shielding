"""Unit tests for Healthcare Clinical PII detection and surrogate generation."""

import pytest
from promptshield.detectors import PIIDetector
from promptshield.redactor import PromptShieldEngine


@pytest.fixture
def detector():
    return PIIDetector(seed=42)


def test_detect_abha_id(detector):
    text = "Patient ABHA ID is 14-8291-0391-4921 registered under ABDM."
    matches = detector.detect_all(text)
    assert len(matches) == 1
    assert matches[0].pii_type == "ABHA"
    assert matches[0].original == "14-8291-0391-4921"


def test_detect_abha_address(detector):
    text = "Send medical records to ramesh9812@abdm for teleconsultation."
    matches = detector.detect_all(text)
    assert len(matches) == 1
    assert matches[0].pii_type == "ABHA"
    assert matches[0].original == "ramesh9812@abdm"


def test_detect_patient_id_and_mrn(detector):
    text = "Admitted under UHID: 984721. Previous MRN: DEL-849204."
    matches = detector.detect_all(text)
    assert len(matches) == 2
    types = [m.pii_type for m in matches]
    assert types == ["PATIENT_ID", "PATIENT_ID"]
    assert matches[0].original == "984721"
    assert matches[1].original == "DEL-849204"


def test_detect_patient_name_header_and_salutation(detector):
    text = "Patient Name: Rajesh Gupta\nAge: 45 Y  Gender: Male"
    matches = detector.detect_all(text)
    assert len(matches) == 1
    assert matches[0].pii_type == "PATIENT_NAME"
    assert matches[0].original == "Rajesh Gupta"

    text2 = "Prescription dispensed for Mrs. Kavita Deshmukh."
    matches2 = detector.detect_all(text2)
    assert len(matches2) == 1
    assert matches2[0].pii_type == "PATIENT_NAME"
    assert "Kavita Deshmukh" in matches2[0].original


def test_detect_doctor_name(detector):
    text = "Consultant: Dr. Arvind Swaminathan, MD Cardiology."
    matches = detector.detect_all(text)
    assert len(matches) >= 1
    doc_matches = [m for m in matches if m.pii_type == "DOCTOR_NAME"]
    assert len(doc_matches) == 1
    assert "Arvind Swaminathan" in doc_matches[0].original


def test_detect_dob(detector):
    text = "DOB: 15/07/1985 | Blood Group: B+ve"
    matches = detector.detect_all(text)
    dob_matches = [m for m in matches if m.pii_type == "DOB"]
    assert len(dob_matches) == 1
    assert dob_matches[0].original == "15/07/1985"


def test_medical_terms_preservation():
    """Verify clinical diagnoses, medications, dosages, and lab values are NOT touched."""
    engine = PromptShieldEngine(seed=42)
    clinical_text = (
        "Patient Name: Ramesh Verma, UHID: 104928.\n"
        "Diagnosis: Acute Myocardial Infarction, Hypertension, Type 2 Diabetes Mellitus.\n"
        "Rx: Tab Metformin 500mg BD, Tab Atorvastatin 40mg OD, Tab Aspirin 75mg OD.\n"
        "Lab: HbA1c 8.4%, Serum Creatinine 1.1 mg/dL, Platelets 220000/mcL."
    )

    redacted = engine.redact(clinical_text)

    # Patient identifiers replaced
    assert "Ramesh Verma" not in redacted
    assert "104928" not in redacted

    # Clinical medical knowledge preserved exactly for LLM reasoning
    assert "Acute Myocardial Infarction" in redacted
    assert "Hypertension" in redacted
    assert "Type 2 Diabetes Mellitus" in redacted
    assert "Tab Metformin 500mg BD" in redacted
    assert "Tab Atorvastatin 40mg OD" in redacted
    assert "HbA1c 8.4%" in redacted
    assert "Serum Creatinine 1.1 mg/dL" in redacted

    # Round trip restore
    restored = engine.restore(redacted)
    assert restored == clinical_text
