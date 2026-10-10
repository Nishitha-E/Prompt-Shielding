"""Adversarial and multi-turn consistency tests for Prompt Shield."""

import pytest
from promptshield.redactor import PromptShieldEngine
from promptshield.audit import TransparencyAudit
from promptshield.verhoeff import generate_verhoeff_number


def test_40_turn_session_consistency():
    """Verify that an identifier receives the exact same surrogate across 40 simulated turns."""
    engine = PromptShieldEngine(seed=42)
    name = "Mr. Ramesh Verma"
    aadhaar_valid = generate_verhoeff_number("23635412891")
    prompt_template = f"Patient {name} with Aadhaar {aadhaar_valid} turn "

    first_redacted = engine.redact(prompt_template + "1")
    first_surrogate_name = engine.mapping[name]
    first_surrogate_aadhaar = engine.mapping[aadhaar_valid]

    for turn in range(2, 41):
        redacted = engine.redact(prompt_template + str(turn))
        assert engine.mapping[name] == first_surrogate_name
        assert engine.mapping[aadhaar_valid] == first_surrogate_aadhaar
        assert first_surrogate_name in redacted
        assert first_surrogate_aadhaar in redacted

        # Ensure restoration is 100% accurate at every turn
        restored = engine.restore(redacted)
        assert name in restored
        assert aadhaar_valid in restored


def test_transparency_audit_html_export(tmp_path):
    """Test generating audit summaries and HTML report."""
    engine = PromptShieldEngine(seed=42)
    orig = "Patient Name: Mr. Suresh Rao | UHID: 981240"
    redacted = engine.redact(orig)

    audit = TransparencyAudit(engine.mapping)
    text_summary = audit.generate_text_summary(orig, redacted)
    assert "PROMPT SHIELD: TRANSPARENCY & AUDIT REPORT" in text_summary
    assert "Mr. Suresh Rao" in text_summary

    html_file = tmp_path / "audit_report.html"
    audit.generate_html_report(orig, redacted, str(html_file))
    assert html_file.exists()
    content = html_file.read_text(encoding="utf-8")
    assert "Prompt Shield: Local Transparency Panel" in content
    assert "Mr. Suresh Rao" in content
