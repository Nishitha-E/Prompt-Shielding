"""Tests for PromptShieldEngine redaction, restoration, and session vault."""

import pytest
import json
from promptshield.redactor import PromptShieldEngine
from promptshield.verhoeff import generate_verhoeff_number


def test_round_trip_redaction_restoration(tmp_path):
    engine = PromptShieldEngine(seed=42)

    valid_aadhaar = generate_verhoeff_number("35129847610")
    fmt_aadhaar = f"{valid_aadhaar[:4]} {valid_aadhaar[4:8]} {valid_aadhaar[8:]}"

    input_prompt = f"Salary slip for ABCDE1234F with Aadhaar {fmt_aadhaar} and email test.user@domain.com."
    
    redacted = engine.redact(input_prompt)
    
    assert fmt_aadhaar not in redacted
    assert "ABCDE1234F" not in redacted
    assert "test.user@domain.com" not in redacted

    # Simulate model response referencing the surrogate
    model_response = f"Analysis completed for account with details: {redacted}"
    restored_response = engine.restore(model_response)

    assert fmt_aadhaar in restored_response
    assert "ABCDE1234F" in restored_response
    assert "test.user@domain.com" in restored_response


def test_session_persistence(tmp_path):
    engine1 = PromptShieldEngine(seed=100)
    pan = "XYZP1234K"
    text = f"PAN is {pan}."

    redacted1 = engine1.redact(text)
    session_file = tmp_path / "session.json"
    engine1.save_session(str(session_file))

    # Second engine instance loading the same session
    engine2 = PromptShieldEngine(seed=999)
    engine2.load_session(str(session_file))

    # Redacting the same text should yield exact same surrogate
    redacted2 = engine2.redact(text)
    assert redacted1 == redacted2

    # Restoring response with engine2 should work
    model_resp = f"Processed {redacted1} successfully."
    assert pan in engine2.restore(model_resp)
