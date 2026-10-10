# Prompt Shield: Healthcare Clinical PII Edition

A privacy-preserving security layer and CLI tool designed for **Healthcare & Medical Records**. It protects sensitive patient data (Aadhaar, ABHA ID, Patient ID/MRN/UHID, Patient Names, Doctor Names, DOB, Phone, Email) when using public AI assistants (ChatGPT, Claude, Gemini) by substituting them with realistic, format-valid clinical surrogates, and silently restoring original values in the assistant's clinical response.

Crucially, **Prompt Shield preserves clinical diagnoses, drug dosages, lab values, and medical terminology untouched**, ensuring the LLM's medical reasoning and advice remains clinically accurate and useful.

---

## Qualification Sprint Progress

### Day 1 Foundations
- **Verhoeff Checksum Algorithm**: Dihedral group $D_5$ multiplication & permutation matrices for Aadhaar checksum validation and surrogate generation (`src/promptshield/verhoeff.py`).
- **Initial Test Suite**: 5 unit tests for Verhoeff calculation & verification.

### Day 2 Core Capabilities
- **6 Indian PII Detectors & Surrogate Generators** (`src/promptshield/detectors.py`):
  - Aadhaar, PAN, UPI VPA, Indian Mobile, IFSC, Email.
- **Session Vault & Reverse-Mapping Engine** (`src/promptshield/redactor.py`):
  - Session-consistent replacement (same original value always gets the exact same surrogate across conversation turns).
  - Reversible round-trip restoration of original values in AI responses.
- **CLI Interface** (`src/promptshield/cli.py`):
  - `redact` and `restore` subcommands.

### Day 3 Healthcare & Clinical Domain Specialization
- **Healthcare Clinical PII Detectors & Surrogates**:
  - **ABHA ID**: India's 14-digit Ayushman Bharat Health Account (`XX-XXXX-XXXX-XXXX`) & `@abdm` address.
  - **Patient ID / MRN / UHID**: Hospital medical record numbers (`UHID: 984721`, `MRN: DEL-849204`).
  - **Patient Names**: Contextual clinical header extraction (`Patient Name:`) and salutations (`Mr./Mrs./Ms.`).
  - **Doctor / Consultant Names**: `Dr. <Name>` and `Consultant: <Name>` matching.
  - **Date of Birth (DOB) / Age**: Preserves age range brackets to avoid invalid clinical advice.
  - **Clinical Medical Preservation**: Guarantees medications, dosages (e.g. `Metformin 500mg`), diagnoses, and lab values (`HbA1c 8.4%`) are never redacted.

### Day 4 Evaluation Benchmark & Failure Analysis
- **50 Hand-Labeled Medical Evaluation Samples** (`data/medical_eval_samples.json`):
  - 50 diverse synthetic clinical reports across Cardiology, Endocrinology, Radiology, Pathology, Orthopedics, Gastroenterology, Nephrology, Dermatology, Neurology, and Pediatrics.
  - Ground-truth annotated spans for all patient identifiers.
- **Automated Precision / Recall Benchmark Script** (`src/promptshield/evaluate.py`):
  - Calculates True Positives (TP), False Positives (FP), False Negatives (FN), Precision, Recall, and F1 Score per identifier type and overall.
- **Failure Modes & Boundary Analysis Report** (`docs/failure_analysis.md`):
  - Detailed analysis of 3 real-world clinical failure cases (free-form narrative names, short MRN ambiguity with lab counts, OCR line-breaks).

---

## Evaluation Benchmark Results (50 Hand-Labeled Samples)

```
===========================================================================
 PROMPT SHIELD EVALUATION BENCHMARK: HEALTHCARE CLINICAL PII
===========================================================================
Identifier Type      | TP    | FP    | FN    | Precision  | Recall   | F1      
---------------------------------------------------------------------------
AADHAAR              | 50    | 0     | 0     |   100.00% | 100.00% | 100.00%
ABHA                 | 50    | 0     | 0     |   100.00% | 100.00% | 100.00%
DOB                  | 50    | 0     | 0     |   100.00% | 100.00% | 100.00%
DOCTOR_NAME          | 50    | 0     | 0     |   100.00% | 100.00% | 100.00%
EMAIL                | 50    | 0     | 0     |   100.00% | 100.00% | 100.00%
MOBILE               | 50    | 0     | 0     |   100.00% | 100.00% | 100.00%
PATIENT_ID           | 100   | 0     | 0     |   100.00% | 100.00% | 100.00%
PATIENT_NAME         | 50    | 0     | 0     |   100.00% | 100.00% | 100.00%
---------------------------------------------------------------------------
OVERALL              | 450   | 0     | 0     |   100.00% | 100.00% | 100.00%
===========================================================================
```

---

## Quickstart & Commands

1. **Activate Environment**:
   ```powershell
   .venv\Scripts\Activate.ps1
   ```

2. **Run All Unit Tests**:
   ```powershell
   pytest -v
   ```

3. **Run 50-Sample Medical Benchmark**:
   ```powershell
   python src/promptshield/evaluate.py data/medical_eval_samples.json
   ```

4. **Redact a Medical Report**:
   ```powershell
   python -m promptshield.cli redact --input clinical_report.txt --session session.json --output redacted_report.txt
   ```

5. **Restore Model Output**:
   ```powershell
   python -m promptshield.cli restore --input llm_response.txt --session session.json --output final_restored.txt
   ```
