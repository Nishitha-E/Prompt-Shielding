"""Tests for Verhoeff algorithm checksum validation and generation."""

import pytest
from promptshield.verhoeff import (
    validate_verhoeff,
    generate_verhoeff_checksum,
    generate_verhoeff_number,
)


def test_validate_verhoeff_valid():
    assert validate_verhoeff("2363") is True
    assert validate_verhoeff("2183") is True


def test_validate_verhoeff_invalid():
    assert validate_verhoeff("2365") is False
    assert validate_verhoeff("12345") is False


def test_generate_verhoeff_checksum():
    assert generate_verhoeff_checksum("236") == 3
    assert generate_verhoeff_checksum("218") == 3


def test_generate_verhoeff_number():
    assert generate_verhoeff_number("236") == "2363"
    assert generate_verhoeff_number("218") == "2183"


def test_validate_generated_verhoeff_numbers():
    for num_str in ["12345678901", "98765432109", "36214589012"]:
        valid_verhoeff = generate_verhoeff_number(num_str)
        assert validate_verhoeff(valid_verhoeff) is True
