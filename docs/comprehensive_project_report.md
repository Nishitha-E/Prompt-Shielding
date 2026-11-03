# Comprehensive Project Report: Prompt Shield

**Project Title**: Prompt Shield: Privacy-Preserving Indian PII Substitution for AI Prompts  
**Domain**: AI Security, Privacy-Enhancing Technologies (PETs), Education Sector Track  
**Program**: Pragya Cyber × Osmania University CCoE · AI Security Internship 2026–27  
**Author / Candidate**: M.Tech Student Researcher  
**Repository**: https://github.com/Nishitha-E/Prompt-Shielding  
**Target Gate**: Gate 0 (Qualification Sprint & Working Prototype)  

---

## 1. Introduction

With the rapid emergence of generative artificial intelligence and Large Language Model (LLM) interfaces such as OpenAI ChatGPT, Anthropic Claude, and Google Gemini, students and university applicants increasingly rely on these tools for academic tasks. Typical use cases include drafting Statements of Purpose (SOP) for postgraduate admissions, applying for state scholarship fee waivers (such as Telangana ePASS), submitting hostel accommodation appeals, and querying complex tuition fee reimbursement procedures.

During these interactions, users routinely paste sensitive, legally protected Personally Identifiable Information (PII) into conversational prompt boxes. This includes national identity numbers (Aadhaar, PAN), contact coordinates (mobile numbers, personal email addresses), banking credentials (bank account numbers, IFSC codes, UPI handles), residential addresses with postal PIN codes, and student identification numbers.

Transmitting raw, unencrypted personal identifiers to third-party commercial LLM providers presents substantial data exposure, regulatory non-compliance, and profiling risks. Under the Digital Personal Data Protection Act (DPDP Act) 2023 of India, processing sensitive personal identifiers requires strict privacy safeguards. Prompt Shield was conceived to bridge this gap: providing an autonomous, client-side security intermediary that enables users to leverage the cognitive reasoning of public LLMs without exposing real Indian PII.

---

## 2. Problem Statement

Existing approaches to privacy preservation in text processing rely predominantly on **irreversible redaction** or **generic masking**. Standard tools detect sensitive strings and replace them with placeholder tokens such as `[REDACTED]`, `[NAME]`, `[PHONE_NUMBER]`, or `XXXX-XXXX-XXXX`.

Through initial empirical investigation on academic prompts, generic token masking was found to suffer from three critical defects:

1. **Syntactic and Grammatical Disruption**: Generic placeholders disrupt the natural syntax and sentence flow, leading language models to produce disjointed, awkward, or grammatically distorted responses.
2. **Degradation of Model Reasoning**: Public LLMs use downstream token representations to reason about entities. Replacing an identifier with `[REDACTED]` strips semantic context. For example, if a student writes *"My sister Priya and I applied under Aadhaar [REDACTED] and [REDACTED]"*, the model cannot track which entity corresponds to which applicant in subsequent conversation turns.
3. **Irreversibility**: Once a prompt is masked with static `[REDACTED]` tokens, the original values cannot be automatically restored into the model's generated advice. The user must manually reconstruct the output to create a usable document.

### The Objective of Prompt Shield:
To develop a lightweight, client-side, zero-exfiltration Python tool that:
* Detects selected Indian personal identifiers with high precision.
* Replaces detected identifiers with **realistic, format-valid synthetic surrogates** that preserve syntax and format (including mathematical checksums).
* Preserves academic and institutional context (e.g., college names, degree programs, CGPA, GATE scores) completely unredacted.
* Maintains session consistency across conversational turns.
* Silently and reversibly restores the original values in the assistant's returned response using a local session vault.

---

## 3. Dataset Selection & Direct Dataset Usage

### Selected Public Dataset:
* **Dataset Name**: Indic Synthetic Profiles (`adwaith06/indic-synthetic-profiles`)
* **Host / Repository**: Hugging Face Datasets Hub
* **Author**: Adwaith A Kumar
* **License**: MIT License
* **Format**: Comma-Separated Values (`data.csv`, 3.4 MB, 10,000 profile records)

### Direct Usage of Dataset Records:
Instead of relying on arbitrary artificial numbers, Prompt Shield incorporates the real records downloaded directly from the official `indic-synthetic-profiles` dataset (`data/indic_synthetic_profiles.csv`).

The evaluation dataset (`data/education_eval_samples.json`) directly pulls fields row-by-row from the dataset:
* `name`: Native and Latin Indian student names (e.g. `Sathish Shivaprasad`, `Vikas Gupta`, `Neha Joshi`).
* `aadhaar`: Genuine 12-digit numbers from the dataset (e.g. `7430 3911 7183`), which strictly satisfy the mathematical **Verhoeff checksum algorithm**.
* `pan`: Indian Income Tax alphanumeric identifiers (e.g. `TDMPR2705I`, `IIBPD7545U`).
* `phone`: 10-digit Indian mobile numbers (e.g. `+91 93834 65787`).
* `email`: Personal student email addresses (e.g. `vikas.gupta@yahoo.com`).
* `bank_account_account` & `bank_account_ifsc`: 11-14 digit bank accounts and RBI-compliant IFSC branch codes (e.g. `ICIC0539131`, `SBIN0759019`).
* `upi_id`: Indian Virtual Payment Addresses (`vikas675@okaxis`, `@oksbi`, `@paytm`, `@ybl`).
* `pincode`: 6-digit postal PIN codes (e.g. `580500`).
* `college` & `degree`: Educational context (e.g. `IIT Guwahati`, `University College of Engineering, Osmania University`, `B.Tech`, `M.E.`).

---

## 4. Solution Architecture

Prompt Shield employs a **reversible, format-preserving substitution pipeline** operating entirely within local volatile memory. The solution architecture is illustrated below:

```
                            [ User's Original Prompt ]
              "Student Name: Mr. Sathish Shivaprasad | Aadhaar: 7430 3911 7183"
                                        │
                                        ▼
             ┌───────────────────────────────────────────────────────┐
             │            Stage 1: Normalization & Ingestion         │
             │   - Heals OCR hyphenations and soft line breaks       │
             └──────────────────────────┬────────────────────────────┘
                                        │
                                        ▼
             ┌───────────────────────────────────────────────────────┐
             │       Stage 2: Deterministic Detection & Validation   │
             │   - Regex recognizers for 9 core Indian PII types     │
             │   - Mathematical Verhoeff Checksum for Aadhaar        │
             │   - Context filtering (preserves Osmania Univ, CGPA)  │
             └──────────────────────────┬────────────────────────────┘
                                        │
                                        ▼
             ┌───────────────────────────────────────────────────────┐
             │     Stage 3: Format-Valid Surrogate Generation        │
             │   - Replaces PII with realistic synthetic values      │
             │   - Validates synthetic Aadhaar check-digit (Verhoeff)│
             └──────────────────────────┬────────────────────────────┘
                                        │
                                        ▼
             ┌───────────────────────────────────────────────────────┐
             │      Stage 4: Local Vault & Outgoing Transmission     │
             │   - Stores {"Sathish Shivaprasad": "Sneha Kulkarni"}  │
             │   - Sends sanitized prompt to Public AI Assistant     │
             └──────────────────────────┬────────────────────────────┘
                                        │
                                        ▼
             ┌───────────────────────────────────────────────────────┐
             │           Stage 5: Silent Reverse Restoration         │
             │   - Intercepts incoming AI Response                   │
             │   - Replaces "Sneha Kulkarni" -> "Sathish Shivaprasad"│
             │   - Presents clean, original document to the user     │
             └───────────────────────────────────────────────────────┘
```

---

## 5. Implementation Details & File Structure

The project is structured as a modular Python package with clean separation of concerns:

```text
prompt-shield/
├── data/
│   ├── indic_synthetic_profiles.csv      # Direct raw dataset from Hugging Face (MIT)
│   └── education_eval_samples.json       # 50 hand-labeled test prompts from the dataset
├── docs/
│   ├── comprehensive_project_report.md   # Complete technical report
│   └── internship_progress_report.md     # Gate 0 Progress & Failure Analysis Report
├── scripts/
│   └── generate_education_dataset.py     # Pulls rows from CSV into 50 evaluation prompts
├── src/
│   └── promptshield/
│       ├── __init__.py                   # Package initializer (__version__ = "0.1.0")
│       ├── cli.py                        # Terminal CLI supporting redact, restore, demo, eval
│       ├── detectors.py                  # Regex patterns, overlap filter & surrogate generators
│       ├── evaluate.py                   # Confusion matrix evaluator (Precision, Recall, F1)
│       ├── redactor.py                   # Local vault, session persistence & reverse restorer
│       └── verhoeff.py                   # Dihedral group D5 Verhoeff checksum algorithm
├── tests/
│   ├── test_detectors.py                 # 9 unit tests for all PII pattern detectors
│   ├── test_redactor.py                  # 4 tests for round-trip restore, persistence, context
│   └── test_verhoeff.py                  # 5 unit tests for mathematical checksum validation
├── .gitignore                            # Excludes .venv, raw CSVs, and cache folders
├── pyproject.toml                        # Package specification and CLI entry point
├── pytest.ini                            # Pytest configuration
└── README.md                             # Quickstart execution guide
```

---

## 6. Code Explanation of Each File

### 1. `src/promptshield/verhoeff.py` (Mathematical Checksum Algorithm)
* **Purpose**: Implements the Verhoeff algorithm to validate 12-digit Indian Aadhaar numbers and generate format-valid Aadhaar surrogates.
* **Dihedral Group $D_5$ Multiplication (`VERHOEFF_D`)**: Uses a non-commutative $10 \times 10$ matrix representing pentagon symmetries. Because $a \times b \neq b \times a$, consecutive transposed digits (e.g. typing `23` instead of `32`) produce different values and are 100% caught.
* **Permutation Table (`VERHOEFF_P`)**: An $8 \times 10$ matrix cyclically shifting digits by position, eliminating symmetry cancellations.
* **`validate_verhoeff(number)`**: Iterates digits from right to left, applies the matrices, and returns `True` if checksum equals 0.
* **`generate_verhoeff_number(number)`**: Computes the required 12th check digit using `VERHOEFF_INV` to create valid synthetic Aadhaar numbers.

### 2. `src/promptshield/detectors.py` (PII Recognizers & Surrogates)
* **Purpose**: Scans text for the 9 core Indian PII types and generates format-valid surrogates.
* **Core Recognizers**:
  * `AADHAAR_PATTERN`: Matches `\b[2-9]\d{3}[\s-]?[0-9]{4}[\s-]?[0-9]{4}\b` and invokes `validate_verhoeff()`.
  * `PAN_PATTERN`: Standard 10-character alphanumeric `[A-Z]{5}[0-9]{4}[A-Z]`.
  * `MOBILE_PATTERN`: Matches 10-digit Indian numbers starting with 6–9 (`(?:\+91[\s-]?)?[6-9](?:[\s-]?\d){9}\b`).
  * `EMAIL_PATTERN`: Standard RFC email format with negative lookahead to exclude banking handles.
  * `UPI_PATTERN`: VPAs ending in Indian banking handles (`@oksbi`, `@okaxis`, `@paytm`, `@ybl`, etc.).
  * `IFSC_PATTERN`: Standard 11-character RBI bank branch codes (`[A-Z]{4}0[A-Z0-9]{6}`).
  * `BANK_ACCOUNT_PATTERN`: 9–18 digits anchored by `Bank A/c No` or `SB A/c`.
  * `PINCODE_PATTERN`: 6-digit postal PIN codes anchored by `PIN Code:`.
  * `NAME_HEADER_PATTERN` & `SALUTATION_NAME_PATTERN`: Header-anchored names (`Student Name:`) and honorific salutations (`Mr.`, `Ms.`).
* **`detect_all(text)`**: Runs all recognizers, validates Aadhaar checksums, and sorts matches by start position, pruning any overlapping duplicate spans.
* **`generate_surrogate(pii_type, original)`**: Generates realistic synthetic replacements preserving original formatting.

### 3. `src/promptshield/redactor.py` (Local Vault & Reverse Restoration)
* **Purpose**: Manages the bidirectional replacement engine and ensures zero network exfiltration.
* **`normalize(text)`**: Upstream cleaner that removes soft hyphens (`\u00ad`) and stitches split digit sequences caused by OCR line breaks.
* **`redact(text)`**: Replaces detected entities from right to left (descending order of start index) to preserve text offsets. Reuses surrogates across multiple occurrences to ensure **session consistency**.
* **`restore(text)`**: Replaces synthetic surrogates back with original user data. Substitutions are ordered in descending order of surrogate length to prevent substring corruption.
* **`save_session(path)` & `load_session(path)`**: Persists mapping dictionaries to local JSON for multi-turn conversations.

### 4. `src/promptshield/cli.py` (Terminal Interface)
* **Purpose**: Provides four terminal commands:
  * `promptshield redact`: Masks input text and outputs local session mapping.
  * `promptshield restore`: Ingests model response and restores original personal data.
  * `promptshield demo`: Runs an automated 4-step live demonstration.
  * `promptshield eval`: Benchmarks performance on the 50 dataset samples.

### 5. `src/promptshield/evaluate.py` (Evaluation Benchmark)
* **Purpose**: Computes True Positives (TP), False Positives (FP), False Negatives (FN), Precision, Recall, and F1 score against ground-truth annotated samples.
* **Results on 50 Dataset Samples**:
  * **Precision**: **98.20%**
  * **Recall**: **93.56%**
  * **F1 Score**: **95.82%**
  * **Total Errors Documented**: 38 (8 False Positives on venue PINs, 30 False Negatives on unanchored narrative names and inline postal codes).

---

## 7. How to Run the Project (CLI Guide)

All commands execute directly in the terminal from the project root `D:\Projects\prompt-shield`:

### 1. Run the Interactive Live Demo:
```powershell
.venv\Scripts\python -m promptshield.cli demo
```
*Executes the 4-step demonstration: Original Text -> Local Redaction -> Simulated LLM Response -> Silent Restoration.*

### 2. Run the 50-Sample Evaluation Benchmark:
```powershell
.venv\Scripts\python -m promptshield.cli eval
```
*Outputs the empirical confusion matrix and Precision/Recall/F1 table.*

### 3. Run Automated Unit Tests:
```powershell
.venv\Scripts\pytest -v
```
*Executes all 18 unit tests across Verhoeff, detectors, and redactor in 0.28 seconds.*

### 4. Redact and Restore Custom Files:
```powershell
# Redact file and store session mapping
.venv\Scripts\python -m promptshield.cli redact -i prompt.txt -o masked.txt -s session.json

# Restore original values in AI response
.venv\Scripts\python -m promptshield.cli restore -i response.txt -o final.txt -s session.json
```

---

## 8. Failure Modes & Boundary Analysis

To ensure an honest, credible evaluation, Prompt Shield explicitly documents its empirical failure cases:

1. **Unanchored Names in Free Narrative Text (Recall: 63.64%)**:
   * *Problem*: In Statement of Purpose (SOP) essays, students mention names naturally: *"I discussed with my guardian Suresh Reddy"*.
   * *Root Cause*: Deterministic regex relies on contextual anchors (`Student Name:`) or honorifics (`Mr./Ms.`). Without these, names are missed.
   * *Why Regex Cannot Solve This*: Matching arbitrary capitalized word pairs (`[A-Z][a-z]+ [A-Z][a-z]+`) causes severe false positives by redacting educational context like `Osmania University` or `Cyber Security`.
2. **Ambiguous 6-Digit Institutional Codes (Precision: 84.62%)**:
   * *Problem*: 6-digit campus venue numbers (`Venue PIN Code: 500045`) trigger the postal PIN regex.
   * *Root Cause*: Postal PIN codes lack mathematical checksums like Aadhaar, requiring semantic dependency parsing.
3. **Inline Postal Codes Missed Without Explicit Keywords (Recall: 88.00%)**:
   * *Problem*: Informal addresses written as `"Hyderabad - 500007"` omit the label `"PIN Code:"`.
   * *Root Cause*: To avoid misclassifying GATE scores or fee sums as PIN codes, the regex enforces anchors, causing bare postal codes to leak.

---

## 9. Future Scope (Phase 2 Roadmap)

Following Gate 0 qualification:

1. **Hybrid Architecture (Regex + Local Lightweight NER)**:
   * Retain fast deterministic regex for checksum-backed identifiers (Aadhaar, PAN, IFSC, Mobile, UPI).
   * Integrate an on-device, quantized token classifier (e.g., 8-bit MobileBERT or BiLSTM-CRF via ONNX Runtime Web) to detect unanchored names in narrative paragraphs without network transmission.
2. **Manifest V3 Browser Extension**:
   * Build a browser extension that intercepts prompt submissions directly inside ChatGPT (`chatgpt.com`), Claude (`claude.ai`), and Gemini (`gemini.google.com`) textareas.
   * Use a `MutationObserver` on streaming LLM responses to silently restore original data before it renders on screen.
3. **Multilingual Native Script Expansion**:
   * Expand detectors to natively support Devanagari, Telugu, and Tamil script names and numerals directly from the Indic Synthetic Profiles dataset.

---

## 10. Conclusion

Prompt Shield proves that privacy preservation for AI prompts does not require destructive token masking (`[REDACTED]`) or reliance on external cloud services. By implementing the Verhoeff mathematical checksum algorithm, deterministic pattern recognizers, and a reversible local session vault, the tool successfully protects sensitive Indian personal identifiers while preserving critical educational context. Evaluated against 50 hand-labeled records directly extracted from the official Indic Synthetic Profiles dataset, Prompt Shield achieves **98.20% Precision**, **93.56% Recall**, and an **F1-score of 95.82%**, fulfilling all Gate 0 requirements and establishing the foundation for Phase 2 browser extension integration.
