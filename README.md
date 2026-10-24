# Prompt Shield: Indian PII Protection for AI Prompts

Prompt Shield is a Python tool designed to protect Indian Personally Identifiable Information (PII) in text prompts sent to AI assistants. It replaces sensitive student and personal data with realistic, format-valid synthetic surrogates, and restores the original values when the AI assistant responds.

## Key Features
- Detects 11 Indian identifier types: Aadhaar, PAN, Mobile, Email, IFSC, Bank Account Number, UPI ID, PIN code, DOB, Student Roll Number, and Student Name.
- Mathematical checksum validation for Aadhaar using the Verhoeff algorithm.
- Reversible local mapping: original data never leaves your computer and is restored silently.
- Preserves academic context such as college names, degree programs, CGPA, and GATE scores.

## Project Structure
```
prompt-shield/
├── data/
│   └── education_eval_samples.json   # 50 hand-labeled test prompts
├── docs/
│   ├── failure_analysis.md           # Analysis of edge case failures
│   └── technical_note.md             # Architecture and design notes
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
Tested against 50 hand-labeled education scenarios:
- Precision: 99.67%
- Recall: 99.34%
- F1 Score: 99.50%
- Documented edge cases: 6-digit rank numbers vs PIN codes, and unanchored names in narrative essays.
