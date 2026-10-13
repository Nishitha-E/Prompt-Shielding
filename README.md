# Prompt Shield: Healthcare Clinical PII Edition

A privacy-preserving security layer and CLI tool designed for **Healthcare & Medical Records**. It protects sensitive patient data (Aadhaar, ABHA ID, Patient ID/MRN/UHID, Patient Names, Doctor Names, DOB, Phone, Email) when using public AI assistants (ChatGPT, Claude, Gemini) by substituting them with realistic, format-valid clinical surrogates, and silently restoring original values in the assistant's clinical response.

Crucially, **Prompt Shield preserves clinical diagnoses, drug dosages, lab values, and medical terminology untouched**, ensuring the LLM's medical reasoning and advice remains clinically accurate and useful.

---

## Qualification Sprint Progress

### Day 1 Foundations (06-10-2026)
- **Verhoeff Checksum Algorithm**: Dihedral group $D_5$ multiplication & permutation matrices for Aadhaar checksum validation and surrogate generation (`src/promptshield/verhoeff.py`).
- **Initial Test Suite**: 5 unit tests for Verhoeff calculation & verification.

### Day 2 Core Capabilities (07-10-2026)
- **6 Indian PII Detectors & Surrogate Generators** (`src/promptshield/detectors.py`):
  - Aadhaar, PAN, UPI VPA, Indian Mobile, IFSC, Email.
- **Session Vault & Reverse-Mapping Engine** (`src/promptshield/redactor.py`):
  - Session-consistent replacement (same original value always gets the exact same surrogate across conversation turns).
  - Reversible round-trip restoration of original values in AI responses.
- **CLI Interface** (`src/promptshield/cli.py`):
  - `redact` and `restore` subcommands.

### Day 3 Healthcare & Clinical Domain Specialization (10-10-2026)
- **Healthcare Clinical PII Detectors & Surrogates**:
  - **ABHA ID**: India's 14-digit Ayushman Bharat Health Account (`XX-XXXX-XXXX-XXXX`) & `@abdm` virtual address.
  - **Patient ID / MRN / UHID**: Hospital medical record identifiers (`UHID: 984721`, `MRN: DEL-849204`).
  - **Patient Names**: Contextual clinical header extraction (`Patient Name:`) and salutations (`Mr./Mrs./Ms.`).
  - **Doctor / Consultant Names**: `Dr. <Name>` and `Consultant: <Name>` matching.
  - **Date of Birth (DOB) / Age**: Preserves age range brackets to avoid invalid clinical advice.
  - **Clinical Medical Preservation**: Guarantees medications, dosages (e.g. `Metformin 500mg`), diagnoses, and lab values (`HbA1c 8.4%`) are never redacted.

### Day 4 Evaluation Benchmark & Failure Analysis (10-10-2026)
- **50 Hand-Labeled Medical Evaluation Samples** (`data/medical_eval_samples.json`):
  - 50 diverse synthetic clinical reports across 10 medical specialties.
  - Ground-truth annotated spans for all patient identifiers.
- **Automated Precision / Recall Benchmark Script** (`src/promptshield/evaluate.py`):
  - Calculates True Positives (TP), False Positives (FP), False Negatives (FN), Precision, Recall, and F1 Score per identifier type and overall.
- **Failure Modes & Boundary Analysis Report** (`docs/failure_analysis.md`):
  - Detailed analysis of 3 real-world clinical failure cases (free-form narrative names, short MRN ambiguity with lab counts, OCR line-breaks).

### Day 5 Transparency Audit, Live Demo, & Gate 0 Technical Note (10-10-2026)
- **Transparency Panel & Audit Subsystem** (`src/promptshield/audit.py`):
  - Generates side-by-side terminal audit reports and exports interactive HTML visual inspection panels (`promptshield audit --html audit.html`).
- **Live Screen-Share Demo Simulator** (`promptshield demo`):
  - Complete 4-step live demonstration harness (Original $\to$ Local Redaction $\to$ Simulated LLM Response $\to$ Silent Restoration) for gate evaluation.
- **Gate 0 Two-Page Technical Note** (`docs/technical_note.md`):
  - Comprehensive write-up covering: what was built, retrospective on what to do differently, and roadmap to scale via Manifest V3 and on-device WebAssembly/WASM.
- **Adversarial & Multi-Turn Stability Suite** (`tests/test_adversarial.py`):
  - Validates 40-turn conversation consistency and audit export.

### Day 6 Latency Benchmarking & Zero-Exfiltration Verification (11-10-2026)
- **Latency & Throughput Profiler** (`src/promptshield/benchmarks.py`):
  - Fulfills the qualification metric: *"Latency low enough that typing never feels delayed"*.
  - Sub-millisecond mean latency (**0.65ms**) and P99 latency (**1.43ms**), well below the 15ms typing threshold.
  - Throughput exceeding 1,000,000 characters/second.
- **Verifiable Zero Network Exfiltration Test** (`tests/test_network_isolation.py`):
  - Intercepts all OS sockets and DNS calls to programmatically prove: *"Nothing leaves the user's machine. This must be demonstrable from the network trace, not merely claimed."*

### Day 7 Upstream Clinical Normalizer & OCR Repair (12-10-2026)
- **Upstream Text Normalizer** (`src/promptshield/normalizer.py`):
  - Directly resolves Failure Mode 3 from `docs/failure_analysis.md`.
  - Automatically heals soft hyphens, OCR line breaks splitting 14-digit ABHA IDs, 12-digit Aadhaar digit blocks, phone numbers, and email strings.
  - Unit tests in `tests/test_normalizer.py`.

### Day 8 Batch Clinical Processing Subsystem (13-10-2026)
- **Bulk Directory Sanitization Engine** (`src/promptshield/batch.py`):
  - Processes entire directories of clinical text files (`.txt`, `.md`, `.json`) with unified session consistency.
  - Generates a machine-readable `batch_manifest.json` recording latency, file count, and mapping metadata.
  - New CLI subcommand: `promptshield batch --input-dir ... --output-dir ...`
  - Comprehensive test suite expanded to **33 passing unit tests**.

---

## Performance & Latency Profile

```
=================================================================
 PROMPT SHIELD: LATENCY & PERFORMANCE PROFILE
=================================================================
Total Test Executions    : 250
Mean Redaction Latency   : 0.648 ms
P50 (Median) Latency     : 0.573 ms
P95 Latency              : 1.079 ms
P99 Latency              : 1.425 ms
-----------------------------------------------------------------
Throughput (Characters)  : 1,027,686 chars/sec
Throughput (Words)       : 149,447 words/sec
Verhoeff Checksum Speed  : 233,104 checks/sec
-----------------------------------------------------------------
Typing Delay Check (<15ms): [PASSED (< 15ms target)]
=================================================================
```

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

2. **Run All 33 Unit Tests**:
   ```powershell
   pytest -v
   ```

3. **Run Performance & Latency Benchmark**:
   ```powershell
   python -m promptshield.cli benchmark
   ```

4. **Run 50-Sample Medical Precision & Recall Benchmark**:
   ```powershell
   python src/promptshield/evaluate.py data/medical_eval_samples.json
   ```

5. **Launch Live Screen-Share Demo**:
   ```powershell
   python -m promptshield.cli demo
   ```

6. **Batch Sanitize a Folder of Documents**:
   ```powershell
   python -m promptshield.cli batch --input-dir raw_records/ --output-dir sanitized_records/ --session batch_session.json
   ```

7. **Generate Transparency Audit & HTML Panel**:
   ```powershell
   python -m promptshield.cli audit --input sample.txt --session session.json --html audit.html
   ```

8. **Redact & Restore Single Files**:
   ```powershell
   python -m promptshield.cli redact --input clinical_report.txt --session session.json --output redacted_report.txt
   python -m promptshield.cli restore --input llm_response.txt --session session.json --output final_restored.txt
   ```
