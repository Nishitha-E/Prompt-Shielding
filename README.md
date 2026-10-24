# Prompt Shield: Indian PII Protection for AI Prompts

Prompt Shield is a Python tool designed to protect Indian Personally Identifiable Information (PII) in text prompts sent to AI assistants. It replaces sensitive student and personal data with realistic, format-valid synthetic surrogates, and restores the original values when the AI assistant responds.

## Key Features
- Detects core Indian identifier types: Aadhaar, PAN, Mobile, Email, IFSC, Bank Account Number, UPI ID, PIN code, and Person Name.
- Mathematical checksum validation for Aadhaar using the Verhoeff algorithm.
- Reversible local mapping: original data never leaves your computer and is restored silently.
- Preserves academic and institutional context such as college names, degree programs, student roll numbers, CGPA, and GATE scores.

## Project Structure
```
prompt-shield/
├── data/
│   └── education_eval_samples.json   # 50 hand-labeled test prompts
├── docs/
│   └── internship_progress_report.md # Complete Gate 0 report & failure analysis
├── src/
│   └── promptshield/
│       ├── __init__.py
│       ├── cli.py                    # Command-line interface
│       ├── detectors.py              # PII regex patterns and surrogates
│       ├── evaluate.py               # Evaluation benchmark script
│       ├── redactor.py               # Masking and reverse mapping engine
│       └── verhoeff.py               # Verhoeff checksum implementation
└── tests/
    ├── test_detectors.py             # PII detector tests
    ├── test_redactor.py              # Redactor and restoration tests
    └── test_verhoeff.py              # Verhoeff algorithm tests
```

## How to Run

### 1. Run Unit Tests
```bash
pytest -v
```

### 2. Run Interactive Live Demo
```bash
python -m promptshield.cli demo
```

### 3. Run Evaluation Benchmark
```bash
python -m promptshield.cli eval
```

### 4. Mask and Restore Text
```bash
# Redact text and save session mapping
python -m promptshield.cli redact -i input.txt -o redacted.txt -s session.json

# Restore original text from AI response
python -m promptshield.cli restore -i model_response.txt -o final.txt -s session.json
```

## Evaluation Results
Tested against 50 hand-labeled education scenarios (incorporating real-world edge cases):
- Precision: 98.20%
- Recall: 93.56%
- F1 Score: 95.82%
- Documented Failures (38 total errors: 8 False Positives, 30 False Negatives):
  - Personal names in narrative statement of purpose (SOP) essays without salutations or headers (Recall: 63.64%).
  - 6-digit campus venue / receipt codes falsely flagged as personal PIN codes (Precision: 84.62%).
  - Inline postal PIN codes without explicit "PIN Code:" keyword.
- Complete report and failure analysis available in `docs/internship_progress_report.md`.
