# Internship Interim Progress Report: Stage 1 & 2
**Project Title**: Prompt Shield — Privacy-Preserving Indian PII Substitution for AI Prompts  
**Domain**: AI Security & Privacy (Education Sector Focus)  
**Selected Dataset**: [Indic Synthetic Profiles](https://huggingface.co/datasets/adwaith06/indic-synthetic-profiles) (`adwaith06/indic-synthetic-profiles` on Hugging Face, MIT License)  
**Internship Program**: Pragya Cyber × Osmania University CCoE · AI Security Internship 2026–27  
**Submitted By**: M.Tech Student Researcher  
**Repository**: [https://github.com/Nishitha-E/Prompt-Shielding](https://github.com/Nishitha-E/Prompt-Shielding)  
**Date**: October 2026  

---

## 1. Problem Statement & Introduction

Public Large Language Models (ChatGPT, Claude, Gemini) are increasingly used by students and university applicants to review statements of purpose (SOP), verify scholarship applications, and draft admission queries. In doing so, users often share sensitive personal identifiers in their prompts.

Conventional redaction methods replace sensitive data with generic tokens like `[REDACTED]` or `[NAME]`, which degrades the grammatical coherence and reasoning ability of the LLM. 

To address this, I am developing **Prompt Shield**. The goal is to detect sensitive Indian personal identifiers in user prompts, substitute them with realistic, format-valid synthetic surrogates, and later restore the original values when the AI assistant returns its response. The original personal data remains local to the user's environment.

---

## 2. Dataset Selection & Domain Scope

For this project, I selected the public, MIT-licensed **Indic Synthetic Profiles** dataset (`adwaith06/indic-synthetic-profiles`) hosted on Hugging Face.

* **Dataset Characteristics**: It contains 10,000 synthetic Indian profile records across 8 Indian languages (Devanagari, Telugu, Tamil, Malayalam, Bengali, Kannada, Gujarati, Marathi) with native scripts, contact details, identity identifiers, and bank details.
* **Why Education Scenarios**: Because the dataset contains structured profile rows rather than conversation logs, I am using these profile schemas to construct realistic education-related prompts (such as admission queries, scholarship forms, and hostel requests).
* **Minimal Indian PII Scope**:
  I identified and scoped the core Indian personal identifiers:
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

## 3. What I Have Implemented So Far

To date, I have completed the foundational dataset setup, mathematical checksum logic, and core PII detection and surrogate generation:

### A. Aadhaar Checksum Engine via Verhoeff Algorithm (`src/promptshield/verhoeff.py`)
To meet the requirement for mathematical validation, I implemented the **Verhoeff algorithm** using dihedral group $D_5$ matrix arithmetic:
* I encoded the multiplication table (`VERHOEFF_D`), permutation matrix (`VERHOEFF_P`), and inverse table (`VERHOEFF_INV`).
* `validate_verhoeff()`: Mathematically verifies whether a 12-digit number has a valid Aadhaar checksum, eliminating false positives on arbitrary 12-digit strings.
* `generate_verhoeff_number()`: Computes the correct Verhoeff check digit so generated synthetic Aadhaar surrogates pass standard validation.
* I verified this implementation with automated unit tests for both valid numbers and corrupted/transposed digits.

### B. Core Indian PII Recognizers & Format-Valid Surrogate Generators (`src/promptshield/detectors.py`)
I implemented deterministic regular expression detectors and format-valid surrogate generators for 9 core Indian PII categories:
1. **Aadhaar**: Matches 12-digit numbers (spaced or hyphenated) and validates them using the Verhoeff checksum.
2. **PAN**: Matches the statutory 10-character alphanumeric structure (`[A-Z]{5}[0-9]{4}[A-Z]`) and generates format-valid synthetic PANs.
3. **Mobile**: Detects 10-digit Indian numbers starting with 6–9 with optional `+91` international prefixes.
4. **Email**: Recognizes standard email formats with common personal domains.
5. **Bank Account**: Detects 9–18 digit account numbers anchored by banking terms (`Bank A/c No`, `Account No`).
6. **IFSC**: Matches the standard 11-character bank branch code (`[A-Z]{4}0[A-Z0-9]{6}`).
7. **UPI ID**: Detects VPAs ending in Indian banking handles (`@oksbi`, `@okhdfcbank`, `@paytm`, `@ybl`).
8. **Postal PIN Code**: Matches 6-digit Indian postal codes (100000–899999).
9. **Personal Names**: Detects names anchored by structured headers (`Student Name:`, `Applicant:`) and Indian salutations (`Mr.`, `Ms.`, `Kumar`, `Kumari`).

Crucially, the detector isolates and protects academic qualifications, college names, and marks from being treated as PII.

---

## 4. Current Work in Progress & Next Steps (To Be Completed for 29th Review)

With the detection and surrogate logic in place, I am now completing the remaining pipeline stages:

### C. Reversible Session Vault & Silent Restoration Engine (`src/promptshield/redactor.py`)
* **Session Consistency**: I am implementing a local mapping store so that if an original identifier appears multiple times across turns, it consistently receives the exact same synthetic surrogate.
* **Exact Restoration**: Building the client-side reverse-mapping engine (`surrogate -> original`) that intercepts the AI assistant's response and restores the original values silently before presentation.
* **Zero Exfiltration**: All session mappings will remain strictly local in memory or in a local session JSON file.

### D. User-Facing Command-Line Interface (`src/promptshield/cli.py`)
* Developing a clean CLI with four commands:
  - `redact`: Mask PII in a file and export the local session mapping.
  - `restore`: Restore original values in the model's response using the session mapping.
  - `demo`: An interactive 4-step demonstration using an Osmania University scholarship inquiry.
  - `eval`: Automated benchmark runner.

### E. Evaluation Benchmark & Failure Case Analysis (`data/` & `tests/`)
* **50 Ground-Truth Test Records**: I am creating 50 hand-labeled synthetic education scenarios modeled after the Indic Synthetic Profiles dataset across 10 academic workflows (admissions, scholarships, hostel allotment, fees, transcripts).
* **Metrics to Report**: I will measure and report Precision, Recall, and F1-score across all supported categories.
* **Failure Analysis**: I will document known real-world edge cases where deterministic rules face challenges—specifically unanchored names in free-form narrative essays (which require future on-device NER) and ambiguous 6-digit campus venue codes versus postal PIN codes.

---

## 5. Summary & Timeline

* **Completed So Far**:
  - Dataset selection and scoping (`adwaith06/indic-synthetic-profiles`).
  - Verhoeff dihedral group $D_5$ algorithm for Aadhaar validation and checksum-valid surrogates.
  - Core Indian PII recognizers and format-preserving synthetic surrogate generators.
* **Target for October 29th Connection**:
  - Complete integration of the reversible session redactor and CLI tool.
  - Finalize benchmark evaluation on the 50 hand-labeled samples and document the failure cases.
  - Prepare a 10-minute live terminal demonstration showing round-trip redaction and restoration.

---
*Report submitted by M.Tech Student Researcher for Pragya Cyber × Osmania University CCoE AI Security Internship.*
