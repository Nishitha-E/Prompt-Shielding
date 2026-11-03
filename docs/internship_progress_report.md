# Internship Progress Report: Stage 1 & 2
**Project Title**: Prompt Shield — Privacy-Preserving Indian PII Substitution for AI Prompts  
**Domain**: AI Security & Privacy (Education Sector Focus)  
**Selected Dataset**: [Indic Synthetic Profiles](https://huggingface.co/datasets/adwaith06/indic-synthetic-profiles) (`adwaith06/indic-synthetic-profiles` on Hugging Face, MIT License)  
**Internship Program**: Pragya Cyber × Osmania University CCoE · AI Security Internship 2026–27  
**Submitted By**: M.Tech Student Researcher  
**Repository**: [https://github.com/Nishitha-E/Prompt-Shielding](https://github.com/Nishitha-E/Prompt-Shielding)  
**Date**: October 2026  

---

## 1. Problem Statement & Introduction

Public Large Language Models (ChatGPT, Claude, Gemini) are frequently used by students and applicants to review statements of purpose (SOP), verify scholarship applications, and draft admission queries. Users often share sensitive personal identifiers in these prompts.

Conventional redaction methods replace sensitive data with generic tokens like `[REDACTED]` or `[NAME]`, which damages the grammatical coherence and reasoning ability of the LLM. 

To address this, I developed **Prompt Shield**. The goal is to detect sensitive Indian personal identifiers in user prompts, substitute them with realistic, format-valid synthetic surrogates, and restore the original values when the AI assistant returns its response. All personal data and session mappings remain strictly local to the user's machine.

---

## 2. Dataset Selection & Domain Scope

For this project, I selected the public, MIT-licensed **Indic Synthetic Profiles** dataset (`adwaith06/indic-synthetic-profiles`) hosted on Hugging Face.

* **Dataset Characteristics**: Contains 10,000 synthetic Indian profile records across 8 Indian languages (Devanagari, Telugu, Tamil, Malayalam, Bengali, Kannada, Gujarati, Marathi) with native scripts, contact details, identity numbers, and bank details.
* **Why Education Scenarios**: Because the raw dataset contains tabular profile records rather than conversational text, I implemented `scripts/generate_education_dataset.py` to sample rows from `data/indic_synthetic_profiles.csv` and construct 50 realistic education-related prompts (`data/education_eval_samples.json`) across 10 academic workflows (admissions, scholarships, hostel allotment, fees, transcripts).
* **Minimal Indian PII Scope**:
  The system identifies and scopes 9 core Indian personal identifiers:
  1. Aadhaar Numbers (with Verhoeff checksum validation)
  2. PAN Identifiers
  3. Indian Mobile Numbers
  4. Email Addresses
  5. Bank Account Numbers
  6. IFSC Codes
  7. UPI IDs
  8. Postal PIN Codes
  9. Personal Names

Educational context—such as university names (*Osmania University*), degree courses (*M.E. Cyber Security*), CGPA (*8.85 / 10.0*), and GATE scores (*680*)—is preserved untouched to ensure the LLM's academic advice remains meaningful.

---

## 3. Core Architecture Implemented

### A. Aadhaar Checksum Engine via Verhoeff Algorithm (`src/promptshield/verhoeff.py`)
To meet the requirement for mathematical validation, I implemented the **Verhoeff algorithm** using dihedral group $D_5$ matrix arithmetic:
* Encoded the multiplication table (`VERHOEFF_D`), permutation matrix (`VERHOEFF_P`), and inverse table (`VERHOEFF_INV`).
* `validate_verhoeff()`: Mathematically verifies whether a 12-digit number has a valid Aadhaar checksum, eliminating false positives on arbitrary 12-digit strings.
* `generate_verhoeff_number()`: Computes the correct Verhoeff check digit so generated synthetic Aadhaar surrogates pass standard validation.
* Verified this implementation with automated unit tests for both valid numbers and corrupted/transposed digits.

### B. Core Indian PII Recognizers & Format-Valid Surrogate Generators (`src/promptshield/detectors.py`)
Implemented deterministic regular expression detectors and format-valid surrogate generators for 9 core Indian PII categories:
1. **Aadhaar**: Matches 12-digit numbers (spaced or hyphenated) and validates them using the Verhoeff checksum.
2. **PAN**: Matches the statutory 10-character alphanumeric structure (`[A-Z]{5}[0-9]{4}[A-Z]`) and generates format-valid synthetic PANs.
3. **Mobile**: Detects 10-digit Indian numbers starting with 6–9 with optional `+91` international prefixes.
4. **Email**: Recognizes standard email formats with common personal domains.
5. **Bank Account**: Detects 9–18 digit account numbers anchored by banking terms (`Bank A/c No`, `Account No`).
6. **IFSC**: Matches the standard 11-character bank branch code (`[A-Z]{4}0[A-Z0-9]{6}`).
7. **UPI ID**: Detects VPAs ending in Indian banking handles (`@oksbi`, `@okhdfcbank`, `@paytm`, `@apl`, etc.).
8. **Postal PIN Code**: Matches 6-digit Indian postal codes (100000–899999).
9. **Personal Names**: Detects names anchored by structured headers (`Student Name:`, `Applicant:`) and Indian salutations (`Mr.`, `Ms.`, `Kumar`, `Kumari`).

Crucially, the detector isolates and protects academic qualifications, college names, and marks from being treated as PII.

### C. Reversible Session Vault & Silent Restoration Engine (`src/promptshield/redactor.py`)
Implemented the core redaction and restoration engine:
* **Session Consistency**: Built a local mapping dictionary so that if an original identifier appears multiple times across turns, it consistently receives the exact same synthetic surrogate.
* **Exact Restoration**: Implemented client-side reverse-mapping (`surrogate -> original`) that intercepts the AI assistant's response and restores the original values silently before presentation. Replacements are ordered by surrogate length in descending order to prevent substring collisions.
* **Zero Network Exfiltration**: All session mappings remain strictly local in memory or can be exported to a local session JSON file. No user data ever leaves the local machine.

---

## 4. Completed Work: Interface, Evaluation & Analysis

All core components, user-facing commands, and benchmark evaluations have been implemented, tested, and verified:

### D. User-Facing Command-Line Interface (`src/promptshield/cli.py`)
Implemented a clean, versatile CLI supporting four commands:
- `redact`: Mask PII from direct text (`-t`), interactive terminal input, or input files (`-i`) and export local session mapping (`-s`).
- `restore`: Reverse-map synthetic surrogates back to original values in the model's response using the session vault.
- `demo`: Interactive 4-step demonstration showing original text, redacted prompt, simulated AI response, and restored final output. Supports:
  - Default randomized profile selection from the dataset.
  - Specific sample selection via `-n / --sample-id` (1 to 50).
  - Custom hand-typed text via `-t / --text`.
  - Live interactive prompt input via `-p / --prompt`.
- `eval`: Automated benchmark runner evaluating precision, recall, and F1 across the 50 dataset scenarios.

### E. Evaluation Benchmark & Failure Case Analysis (`data/` & `docs/`)
* **50 Ground-Truth Test Records (`data/education_eval_samples.json`)**: Generated 50 realistic education scenarios directly from `data/indic_synthetic_profiles.csv` across 10 academic workflows (scholarships, hostel allotment, admissions, fee payments, document verification).
* **Quantitative Benchmark Results**:
  - Precision: **98.20%**
  - Recall: **93.56%**
  - F1 Score: **95.82%**
* **Documented Failure Cases (`docs/failure_analysis.md`)**:
  - Categorized 38 total boundary errors (8 False Positives, 30 False Negatives).
  - Addressed unanchored student names in unstructured narrative SOPs (Recall: 63.49%).
  - Handled 6-digit campus venue/token numbers versus postal PIN codes (Precision: 84.62%).

---

## 5. Summary & Milestones Achieved

* **Completed Deliverables**:
  - Dataset integration and scenario generator using `adwaith06/indic-synthetic-profiles`.
  - Verhoeff dihedral group $D_5$ algorithm for Aadhaar validation and checksum-valid surrogates.
  - 9 core Indian PII recognizers and format-preserving synthetic surrogate generators.
  - Reversible session engine with local vault and collision-free round-trip restoration.
  - Full CLI with support for file I/O, direct text flags (`-t`), interactive prompts (`-p`), and dataset sample IDs (`-n`).
  - Comprehensive automated test suite (18 unit tests, all passing).
  - Detailed documentation: `README.md`, `docs/comprehensive_project_report.md`, and `docs/failure_analysis.md`.

---
*Report submitted by M.Tech Student Researcher for Pragya Cyber × Osmania University CCoE AI Security Internship.*
