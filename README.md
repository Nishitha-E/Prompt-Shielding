# Prompt Shield: Education Sector Indian PII Protection

A privacy-preserving security layer and CLI tool designed for **Education Scenarios (Admissions, Scholarships, Student Enquiries)**. It protects sensitive student and applicant data (Aadhaar, PAN, Bank Account Numbers, Roll/Application Numbers, Student Names, DOB, Mobile, Email, UPI, Postal PIN Codes) when using public AI assistants (ChatGPT, Claude, Gemini) by substituting them with realistic, format-valid surrogates, and silently restoring original values in the assistant's response.

**Selected Dataset Reference**: [Indic Synthetic Profiles (Hugging Face: adwaith06/indic-synthetic-profiles)](https://huggingface.co/datasets/adwaith06/indic-synthetic-profiles) — 10,000 synthetic Indian profile records across 23 fields and 8 languages under MIT license.

Crucially, **Prompt Shield preserves institutional context, degree programs, GATE scores, CGPA, and scholarship fee details untouched**, ensuring the LLM's academic and advisory reasoning remains valid and useful.

---

## Qualification Sprint Progress

### Day 1 Foundations (06-10-2026)
- **Verhoeff Checksum Algorithm**: Dihedral group $D_5$ multiplication & permutation matrices for Aadhaar checksum validation and surrogate generation (`src/promptshield/verhoeff.py`).
- **Initial Test Suite**: 5 unit tests for Verhoeff calculation & verification.

### Day 2 Core Capabilities (07-10-2026)
- **Core Indian PII Detectors & Surrogate Generators** (`src/promptshield/detectors.py`):
  - Aadhaar, PAN, UPI VPA, Indian Mobile, IFSC, Email.
- **Session Vault & Reverse-Mapping Engine** (`src/promptshield/redactor.py`):
  - Session-consistent replacement (same original value always gets the exact same surrogate across conversation turns).
  - Reversible round-trip restoration of original values in AI responses.
- **CLI Interface** (`src/promptshield/cli.py`):
  - `redact` and `restore` subcommands.

### Day 3 Education & Student Domain Specialization (10-10-2026)
- **Education Sector PII Detectors & Surrogates**:
  - **Student Roll & Application IDs**: University roll numbers (`Roll No: 1005-26-701`) and application IDs (`OU26-49102`).
  - **Student Names**: Contextual header extraction (`Student Name:`) and salutations (`Mr./Ms./Kumar/Kumari`).
  - **Bank Account & Postal PIN Codes**: Bank A/c numbers for scholarships and 6-digit postal PIN codes.
  - **Academic Knowledge Preservation**: Guarantees college names (*Osmania University*), degree courses (*M.E. Cyber Security*), CGPA (*8.85 / 10.0*), GATE scores (*680*), and fee waivers are never redacted.

### Day 4 Evaluation Benchmark & Failure Analysis (10-10-2026)
- **50 Hand-Labeled Education Evaluation Samples** (`data/education_eval_samples.json`):
  - 50 diverse synthetic education records modeled after Indic Synthetic Profiles across 10 academic scenarios (Admissions, Scholarships, Hostels, Exams, Placement, Bonafide transcripts, Fee UPI, etc.).
  - Ground-truth annotated spans for all student identifiers.
- **Automated Precision / Recall Benchmark Script** (`src/promptshield/evaluate.py`):
  - Calculates True Positives (TP), False Positives (FP), False Negatives (FN), Precision, Recall, and F1 Score per identifier type and overall.
- **Failure Modes & Boundary Analysis Report** (`docs/failure_analysis.md`):
  - Detailed analysis of 3 real-world failure cases (free-form narrative names in SOP essays, PIN code vs rank ambiguity, OCR line-breaks).

### Day 5 Transparency Audit, Live Demo, & Gate 0 Technical Note (10-10-2026)
- **Transparency Panel & Audit Subsystem** (`src/promptshield/audit.py`):
  - Generates side-by-side terminal audit reports and exports interactive HTML visual inspection panels (`promptshield audit --html audit.html`).
- **Live Screen-Share Demo Simulator** (`promptshield demo`):
  - Complete 4-step live demonstration harness (Original $\to$ Local Redaction $\to$ Simulated LLM Response $\to$ Silent Restoration) for gate evaluation.
- **Gate 0 Technical Note** (`docs/technical_note.md`):
  - Comprehensive write-up covering: what was built, retrospective on what to do differently, and roadmap to scale via Manifest V3 and on-device WebAssembly/WASM.
- **Adversarial & Multi-Turn Stability Suite** (`tests/test_adversarial.py`):
  - Validates 40-turn conversation consistency and audit export.

### Day 6 Latency Benchmarking & Zero-Exfiltration Verification (11-10-2026)
- **Latency & Throughput Profiler** (`src/promptshield/benchmarks.py`):
  - Fulfills the qualification metric: *"Latency low enough that typing never feels delayed"*.
  - Sub-millisecond mean latency (**0.39ms**) and P99 latency (**0.76ms**), well below the 15ms typing threshold.
  - Throughput exceeding 1,700,000 characters/second.
- **Verifiable Zero Network Exfiltration Test** (`tests/test_network_isolation.py`):
  - Intercepts all OS sockets and DNS calls to programmatically prove: *"Nothing leaves the user's machine. This must be demonstrable from the network trace, not merely claimed."*

### Day 7 Upstream Clinical & Document Normalizer (12-10-2026)
- **Upstream Text Normalizer** (`src/promptshield/normalizer.py`):
  - Directly resolves Failure Mode 3 from `docs/failure_analysis.md`.
  - Automatically heals soft hyphens, OCR line breaks splitting 12-digit Aadhaar digit blocks, student roll numbers, phone numbers, and email strings.
  - Unit tests in `tests/test_normalizer.py`.

### Day 8 Batch Directory Processing Subsystem (13-10-2026)
- **Bulk Directory Sanitization Engine** (`src/promptshield/batch.py`):
  - Processes entire directories of education records (`.txt`, `.md`, `.json`) with unified session consistency.
  - Generates a machine-readable `batch_manifest.json` recording latency, file count, and mapping metadata.
  - CLI subcommand: `promptshield batch --input-dir ... --output-dir ...`

### Day 9 Tabular & CSV Dataset Sanitizer (18-10-2026)
- **Structured CSV Medical & Student Table Sanitizer** (`src/promptshield/tabular.py`):
  - Processes tabular student profiles (like Indic Synthetic Profiles CSVs) preserving academic columns while redacting student PII.
  - Test suite in `tests/test_tabular.py`.

### Day 10 Interim Progress Report & Tabular CLI (23-10-2026)
- **Formal Interim Report** (`docs/interim_report.md`):
  - Comprehensive report on problem formulation, bidirectional surrogate architecture, benchmark results, and Phase 1 roadmap.
- **Tabular CLI Command** (`promptshield tabular`):
  - Direct command-line interface for sanitizing education CSV datasets.
- **Test Suite**: 31 unit tests passing in 0.32s (`pytest -v`).

---

## Evaluation Benchmark Results (50 Hand-Labeled Samples)

```
===========================================================================
 PROMPT SHIELD EVALUATION BENCHMARK: EDUCATION SECTOR PII
===========================================================================
Identifier Type      | TP    | FP    | FN    | Precision  | Recall   | F1      
---------------------------------------------------------------------------
AADHAAR              | 50    | 0     | 0     |   100.00% | 100.00% | 100.00%
BANK_ACCOUNT         | 50    | 0     | 0     |   100.00% | 100.00% | 100.00%
DOB                  | 50    | 0     | 0     |   100.00% | 100.00% | 100.00%
EMAIL                | 50    | 0     | 0     |   100.00% | 100.00% | 100.00%
IFSC                 | 50    | 0     | 0     |   100.00% | 100.00% | 100.00%
MOBILE               | 50    | 0     | 0     |   100.00% | 100.00% | 100.00%
PAN                  | 50    | 0     | 0     |   100.00% | 100.00% | 100.00%
PINCODE              | 50    | 0     | 0     |   100.00% | 100.00% | 100.00%
STUDENT_ID           | 100   | 0     | 0     |   100.00% | 100.00% | 100.00%
STUDENT_NAME         | 50    | 0     | 0     |   100.00% | 100.00% | 100.00%
UPI                  | 50    | 0     | 0     |   100.00% | 100.00% | 100.00%
---------------------------------------------------------------------------
OVERALL              | 600   | 0     | 0     |   100.00% | 100.00% | 100.00%
===========================================================================
```

---

## Performance & Latency Profile

```
=================================================================
 PROMPT SHIELD: LATENCY & PERFORMANCE PROFILE
=================================================================
Total Test Executions    : 250
Mean Redaction Latency   : 0.391 ms
P50 (Median) Latency     : 0.352 ms
P95 Latency              : 0.587 ms
P99 Latency              : 0.756 ms
-----------------------------------------------------------------
Throughput (Characters)  : 1,710,272 chars/sec
Throughput (Words)       : 248,710 words/sec
Verhoeff Checksum Speed  : 258,959 checks/sec
-----------------------------------------------------------------
Typing Delay Check (<15ms): [PASSED (< 15ms target)]
=================================================================
```

---

## Quickstart & Commands

1. **Activate Environment**:
   ```powershell
   .venv\Scripts\Activate.ps1
   ```

2. **Run All 31 Unit Tests**:
   ```powershell
   pytest -v
   ```

3. **Launch Live Screen-Share Demo**:
   ```powershell
   python -m promptshield.cli demo
   ```

4. **Run 50-Sample Education Precision & Recall Benchmark**:
   ```powershell
   python src/promptshield/evaluate.py data/education_eval_samples.json
   ```

5. **Run Performance & Latency Benchmark**:
   ```powershell
   python -m promptshield.cli benchmark
   ```

6. **Batch Sanitize a Folder of Student Documents**:
   ```powershell
   python -m promptshield.cli batch --input-dir raw_records/ --output-dir sanitized_records/ --session batch_session.json
   ```

7. **Sanitize a Student Profile CSV Dataset**:
   ```powershell
   python -m promptshield.cli tabular --input student_profiles.csv --output sanitized_profiles.csv --session tabular_session.json
   ```

8. **Generate Transparency Audit & HTML Panel**:
   ```powershell
   python -m promptshield.cli audit --input student_prompt.txt --session session.json --html audit.html
   ```

9. **Redact & Restore Single Files**:
   ```powershell
   python -m promptshield.cli redact --input student_prompt.txt --session session.json --output redacted_prompt.txt
   python -m promptshield.cli restore --input llm_response.txt --session session.json --output final_restored.txt
   ```
