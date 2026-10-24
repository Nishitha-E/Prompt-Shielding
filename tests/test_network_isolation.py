"""Verifiable Network Isolation & Zero-Exfiltration Tests for Prompt Shield.

Measures the core qualification criterion:
'Nothing leaves the user's machine. This must be demonstrable from the network trace, not merely claimed.'
"""

import socket
import urllib.request
import pytest
from promptshield.redactor import PromptShieldEngine


class NetworkAccessException(Exception):
    """Raised when an unauthorized outbound network call is detected."""
    pass


def test_zero_network_exfiltration_guarantee(monkeypatch):
    """Assert that zero socket creation, DNS resolution, or network I/O occurs during redaction or restoration."""
    sockets_created = []

    # Mock socket constructor to intercept all network activity
    orig_socket = socket.socket

    def guarded_socket(*args, **kwargs):
        raise NetworkAccessException("CRITICAL: Outbound network socket initiated during local PII processing!")

    monkeypatch.setattr(socket, "socket", guarded_socket)

    # Test engine with dense clinical document containing multiple sensitive PII fields
    engine = PromptShieldEngine(seed=42)
    sample_text = (
        "--- UNIVERSITY ADMISSION ENQUIRY ---\n"
        "Student Name: Mr. Suresh Rao\n"
        "Roll No: 1005-26-701 | Application No: OU26-49102\n"
        "Aadhaar: 2363 5412 8915 | PAN: ABCPK1234Z\n"
        "Contact: 9876543210 | Email: suresh.rao@domain.com\n"
        "Course: M.E. Cyber Security, Osmania University.\n"
        "GATE Score: 680, CGPA: 8.85 / 10.0."
    )

    # Redact must run without attempting any network I/O
    redacted = engine.redact(sample_text)
    assert "Suresh Rao" not in redacted
    assert "2363 5412 8915" not in redacted

    # Restore must also run 100% locally
    restored = engine.restore(redacted)
    assert "Suresh Rao" in restored
    assert "2363 5412 8915" in restored


def test_no_external_dns_resolution(monkeypatch):
    """Verify that no DNS lookups (e.g. getaddrinfo, gethostbyname) are attempted."""
    def guarded_getaddrinfo(*args, **kwargs):
        raise NetworkAccessException("CRITICAL: External DNS resolution attempted!")

    monkeypatch.setattr(socket, "getaddrinfo", guarded_getaddrinfo)
    monkeypatch.setattr(socket, "gethostbyname", guarded_getaddrinfo)

    engine = PromptShieldEngine(seed=42)
    sample = "Patient email: test.user@gmail.com with UPI user@okhdfcbank"
    redacted = engine.redact(sample)
    restored = engine.restore(redacted)

    assert "test.user@gmail.com" in restored
