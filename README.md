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
  - **ABHA ID**: India's 14-digit Ayushman Bharat Health Account (`XX-XXXX-XXXX-XXXX`) & `@abdm` virtual address.
  - **Patient ID / MRN / UHID**: Hospital medical record identifiers (`UHID: 984721`, `MRN: DEL-849204`).
  - **Patient Names**: Contextual clinical header extraction (`Patient Name:`) and salutations (`Mr./Mrs./Ms.`).
  - **Doctor / Consultant Names**: `Dr. <Name>` and `Consultant: <Name>` matching.
  - **Date of Birth (DOB) / Age**: Preserves age range brackets to avoid invalid clinical advice.
  - **Clinical Medical Preservation**: Guarantees medications, dosages (e.g. `Metformin 500mg`), diagnoses, and lab values (`HbA1c 8.4%`) are never redacted.

### Day 4 Evaluation Benchmark & Failure Analysis
- **50 Hand-Labeled Medical Evaluation Samples** (`data/medical_eval_samples.json`):
  - 50 diverse synthetic clinical reports across 10 medical specialties.
  - Ground-truth annotated spans for all patient identifiers.
- **Automated Precision / Recall Benchmark Script** (`src/promptshield/evaluate.py`):
  - Calculates True Positives (TP), False Positives (FP), False Negatives (FN), Precision, Recall, and F1 Score per identifier type and overall.
- **Failure Modes & Boundary Analysis Report** (`docs/failure_analysis.md`):
  - Detailed analysis of 3 real-world clinical failure cases (free-form narrative names, short MRN ambiguity with lab counts, OCR line-breaks).

### Day 5 Transparency Audit, Live Demo, & Gate 0 Technical Note
- **Transparency Panel & Audit Subsystem** (`src/promptshield/audit.py`):
  - Generates side-by-side terminal audit reports and exports interactive HTML visual inspection panels (`promptshield audit --html audit.html`).
- **Live Screen-Share Demo Simulator** (`promptshield demo`):
  - Complete 4-step live demonstration harness (Original $\to$ Local Redaction $\to$ Simulated LLM Response $\to$ Silent Restoration) for gate evaluation.
- **Gate 0 Two-Page Technical Note** (`docs/technical_note.md`):
  - Comprehensive write-up covering: what was built, retrospective on what to do differently, and roadmap to scale via Manifest V3 and on-device WebAssembly/WASM.
- **Adversarial & Multi-Turn Stability Suite** (`tests/test_adversarial.py`):
  - Validates 40-turn conversation consistency and audit export.

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

4. **Launch Live Screen-Share Demo**:
   ```powershell
   python -m promptshield.cli demo
   ```

5. **Generate Transparency Audit & HTML Panel**:
   ```powershell
   python -m promptshield.cli audit --input sample.txt --session session.json --html audit.html
   ```

6. **Redact & Restore Files**:
   ```powershell
   python -m promptshield.cli redact --input clinical_report.txt --session session.json --output redacted_report.txt
   python -m promptshield.cli restore --input llm_response.txt --session session.json --output final_restored.txt
   ```
