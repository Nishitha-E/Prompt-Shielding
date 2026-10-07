# Prompt Shield

A privacy-preserving security layer and CLI tool that sits between users and web-based AI assistants. It automatically detects Indian personal identifiers (PII), replaces them with realistic, format-valid surrogates before sending prompts to LLMs, and silently restores original values in the assistant's response.

---

## Qualification Sprint Features

### Day 1 Foundations
- **Verhoeff Checksum Algorithm**: Dihedral group $D_5$ multiplication & permutation matrices for Aadhaar checksum validation and surrogate generation (`src/promptshield/verhoeff.py`).
- **Initial Test Suite**: 5 unit tests for Verhoeff calculation & verification.

### Day 2 Core Capabilities
- **6 Indian PII Detectors & Surrogate Generators** (`src/promptshield/detectors.py`):
  - **Aadhaar Number**: Detects 12-digit numbers, validates Verhoeff checksums, generates format-valid surrogates.
  - **PAN Card**: Detects 10-character `[A-Z]{5}[0-9]{4}[A-Z]` strings and generates valid PAN format.
  - **UPI VPA**: Detects handles (`@okhdfcbank`, `@ybl`, `@paytm`, etc.) and generates format-valid VPAs.
  - **Indian Mobile**: Detects 10-digit mobile numbers (including `+91` prefix variations).
  - **IFSC Code**: Detects 11-character bank branch codes.
  - **Email Address**: Detects emails and generates domain-consistent surrogates.
- **Session Vault & Reverse-Mapping Engine** (`src/promptshield/redactor.py`):
  - Session-consistent replacement (e.g. same original value always gets the exact same surrogate across conversation turns).
  - High-fidelity restoration of original values in AI responses.
  - Export/import session mapping tables to/from JSON files.
- **CLI Interface** (`src/promptshield/cli.py`):
  - `redact`: Redacts PII from text/file and updates session vault.
  - `restore`: Reverses surrogates in model output back to original PII values.
- **Comprehensive Test Suite**: 14 unit tests covering detection, surrogate validity, session vault persistence, and round-trip restoration.

---

## Setup & Quickstart

1. **Activate virtual environment**:
   ```powershell
   .venv\Scripts\Activate.ps1
   ```

2. **Install in editable mode**:
   ```powershell
   pip install -e .
   ```

3. **Run Unit Tests**:
   ```powershell
   pytest -v
   ```

---

## CLI Usage

### 1. Redact Prompt PII
```powershell
python -m promptshield.cli redact --input input_prompt.txt --session session.json --output redacted_prompt.txt
```

### 2. Restore Original PII in Model Output
```powershell
python -m promptshield.cli restore --input model_response.txt --session session.json --output restored_response.txt
```
