# Prompt Shield

A privacy-preserving security layer and browser extension that detects Indian personal identifiers (PII), replaces them with consistent format-valid surrogates, and reverses the mapping accurately.

## Qualification Sprint - Day 1

Features:
- Verhoeff algorithm implementation for checksum validation and surrogate generation (Aadhaar).
- Automated unit test suite with `pytest`.

## Setup & Running Tests

1. Activate virtual environment:
   ```powershell
   .venv\Scripts\Activate.ps1
   ```
2. Run tests:
   ```powershell
   pytest -v
   ```
