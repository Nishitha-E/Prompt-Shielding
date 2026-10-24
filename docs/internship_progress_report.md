# Internship Progress & Technical Failure Report: Gate 0
**Project Title**: Prompt Shield — Privacy-Preserving Indian PII Substitution for AI Prompts  
**Domain**: AI Security & Privacy (Education Sector Focus)  
**Selected Dataset**: [Indic Synthetic Profiles](https://huggingface.co/datasets/adwaith06/indic-synthetic-profiles) (`adwaith06/indic-synthetic-profiles` on Hugging Face, MIT License)  
**Internship Program**: Pragya Cyber × Osmania University CCoE · AI Security Internship 2026–27  
**Submitted By**: M.Tech Student Researcher  
**Repository**: [https://github.com/Nishitha-E/Prompt-Shielding](https://github.com/Nishitha-E/Prompt-Shielding)  
**Date**: October 2026  

---

## 1. Problem Statement & My Approach

When students and applicants use public Large Language Models (such as ChatGPT, Claude, or Gemini) to draft admission statements of purpose (SOP), verify scholarship eligibility, or query fee structures, they frequently include sensitive personal identifiers in their prompts. Transmitting these values to external AI providers poses privacy and compliance risks.

Traditional redaction tools replace sensitive data with generic tokens like `[REDACTED]` or `[NAME]`. In my initial experiments, I found that this breaks the sentence structure and damages the LLM's reasoning capability. 

To solve this, I designed **Prompt Shield**. My approach is based on three core principles:
1. **Format-Preserving Synthetic Substitution**: Instead of masking, I replace sensitive identifiers with realistic synthetic values that preserve the expected format (for example, generating a valid 12-digit Aadhaar number with a correct checksum).
2. **Reversible Local Vault**: I store the mapping between original values and synthetic surrogates locally in memory (or in a local session JSON file). When the LLM responds referencing the surrogate, my tool silently restores the student's real data. No real personal data ever leaves the user's machine.
3. **Academic Context Preservation**: I specifically configured the engine to preserve educational context—such as university names (*Osmania University*), degree programs (*M.E. Cyber Security*), CGPA (*8.85 / 10.0*), and GATE scores (*680*)—so that the assistant's advisory output remains intact.

---

## 2. Dataset Selection & Scope

For this work, I selected the public, MIT-licensed **Indic Synthetic Profiles** dataset (`adwaith06/indic-synthetic-profiles`) created by Adwaith A Kumar on Hugging Face. 

* **Why I selected this dataset**: It contains 10,000 synthetic Indian profile records covering 8 Indian languages and native scripts (Devanagari, Telugu, Tamil, Malayalam, Bengali, Kannada, Gujarati, Marathi) with realistic Indian names, addresses, phone numbers, identity numbers, and bank details.
* **How I used it**: Because the dataset contains structured tabular rows rather than conversational text, I extracted realistic profile values to construct 50 representative student prompts across 10 common university scenarios: PG admissions, state ePASS scholarships, hostel allotments, duplicate hall tickets, campus placements, education loans, official transcripts, tuition fee UPI payments, library clearance, and marks re-evaluation.
* **Scope of Minimal Indian PII**:
  I focused strictly on the core Indian personal identifiers:
  1. Aadhaar Numbers (with checksum validation)
  2. PAN Identifiers
  3. Indian Mobile Numbers
  4. Email Addresses
  5. Bank Account Numbers
  6. IFSC Codes
  7. UPI IDs
  8. Postal PIN Codes
  9. Personal Names

Academic credentials (college, degree, roll number, marks, and GATE scores) were deliberately kept unredacted.

---

## 3. What I Have Implemented So Far

Over the course of the qualification sprint, I built and verified the following components step-by-step:

### A. Aadhaar Checksum Engine via Verhoeff Algorithm (`src/promptshield/verhoeff.py`)
To satisfy the requirement of mathematical validation, I implemented the **Verhoeff algorithm** from scratch using the dihedral group $D_5$.
* I encoded the multiplication table (`VERHOEFF_D`), permutation matrix (`VERHOEFF_P`), and inverse array (`VERHOEFF_INV`).
* My function `validate_verhoeff()` checks whether an incoming 12-digit string satisfies the checksum condition.
* My function `generate_verhoeff_number()` computes the check digit and generates realistic, format-valid synthetic Aadhaar numbers for surrogacy.

### B. Core Indian PII Recognizers & Surrogate Generators (`src/promptshield/detectors.py`)
I implemented deterministic regular expression patterns and synthetic surrogate generators for each of the 9 core Indian PII categories:
* **Aadhaar**: Matches 12 digits (with optional spaces or dashes) and validates using Verhoeff.
* **PAN**: Matches `[A-Z]{5}[0-9]{4}[A-Z]`.
* **Mobile**: Matches 10-digit mobile numbers starting with 6–9, with optional `+91` prefix.
* **Email**: Matches standard RFC email patterns.
* **Bank Account**: Matches 9–18 digit numbers following bank account keywords.
* **IFSC**: Matches the standard 11-character bank branch pattern (`[A-Z]{4}0[A-Z0-9]{6}`).
* **UPI**: Matches VPAs ending with Indian banking and wallet handles (`@oksbi`, `@okhdfcbank`, `@paytm`, `@ybl`).
* **PIN Code**: Matches 6-digit postal codes starting with digits 1–8.
* **Names**: Matches names preceded by structured headers (`Student Name:`, `Applicant:`) and honorifics (`Mr.`, `Ms.`, `Kumar`, `Kumari`).

### C. Reversible Session Redactor (`src/promptshield/redactor.py`)
* **Session Consistency**: I built a mapping dictionary so that if an original identifier appears multiple times in the prompt, it consistently receives the exact same synthetic surrogate.
* **Reverse Mapping**: I stored the inverse mapping (`surrogate -> original`) and sorted replacements by string length in descending order before replacing, avoiding substring truncation bugs.
* **Zero Network Exfiltration**: All session mappings stay local in memory or are saved to a user-specified session JSON file.

### D. Command-Line Interface (`src/promptshield/cli.py`)
I created an `argparse`-based CLI supporting four straightforward commands:
* `redact`: Redacts a prompt file and saves the session vault.
* `restore`: Reads an AI assistant's response and restores the original data.
* `demo`: Runs an interactive 4-step demonstration using an Osmania University M.E. Cyber Security scholarship query.
* `eval`: Executes an automated benchmark against the 50 hand-labeled samples.

### E. Evaluation Suite & Test Coverage (`tests/`)
* I hand-labeled 50 synthetic student prompts in `data/education_eval_samples.json`.
* I wrote 18 automated unit tests across `test_verhoeff.py`, `test_detectors.py`, and `test_redactor.py`.
* All 18 tests pass in **0.09 seconds** via `pytest`.

---

## 4. Benchmark Results on 50 Hand-Labeled Samples

I ran my benchmark script (`python -m promptshield.cli eval`) against the 50 ground-truth samples (466 total entities):

```
Identifier       TP    FP    FN    Precision  Recall   F1      
AADHAAR          50    0     0       100.00% 100.00% 100.00%
BANK_ACCOUNT     50    0     0       100.00% 100.00% 100.00%
EMAIL            50    0     0       100.00% 100.00% 100.00%
IFSC             50    0     0       100.00% 100.00% 100.00%
MOBILE           50    0     0       100.00% 100.00% 100.00%
NAME             42    0     24      100.00%  63.64%  77.78%
PAN              50    0     0       100.00% 100.00% 100.00%
PINCODE          44    8     6        84.62%  88.00%  86.27%
UPI              50    0     0       100.00% 100.00% 100.00%
-----------------------------------------------------------------
OVERALL          436   8     30       98.20%  93.56%  95.82%
```

* **True Positives (TP)**: 436
* **False Positives (FP)**: 8
* **False Negatives (FN)**: 30
* **Overall Precision**: **98.20%**
* **Overall Recall**: **93.56%**
* **Overall F1 Score**: **95.82%**

---

## 5. What Went Wrong: Honest Technical Failure Analysis

Rather than claiming that everything worked perfectly, I documented the exact edge cases and limitations of my regex-based implementation:

### Failure Case 1: Low Recall on Unanchored Names in Narrative Text (Recall: 63.64%)
* **What Happened**: The detector missed **24 out of 66 personal names** (False Negatives).
* **Why It Failed**: In narrative admission letters and SOP paragraphs, students write natural statements such as:
  > *"I discussed my admission with my guardian Suresh Reddy."*  
  > *"I, Ananya Verma, submit this form for fee verification."*
  Because `Suresh Reddy` and `Ananya Verma` do not have a preceding `Student Name:` header or honorific salutation (`Mr./Ms.`), my regex rules ignored them.
* **Why Regex Cannot Solve This**: If I relax the regex to match any two capitalized words (`[A-Z][a-z]+ [A-Z][a-z]+`), it immediately over-redacts legitimate context like `Osmania University`, `Cyber Security`, `State Government`, and `Advanced Cryptography`. Detecting unanchored names in free-form narrative text fundamentally requires a Named Entity Recognition (NER) model.

### Failure Case 2: Ambiguous 6-Digit Campus Codes Flagged as PIN Codes (Precision: 84.62%)
* **What Happened**: The detector produced **8 False Positives** on PIN codes.
* **Why It Failed**: In student inquiries, 6-digit numbers often appear as campus test venue codes, exam hall tokens, or bank fee counters (e.g., `Venue PIN Code: 500045`). The PIN code pattern matched these numbers.
* **Impact**: While redacting a public hall code does not leak privacy, it removes location context, which can cause the AI assistant to give confused directions.

### Failure Case 3: Inline Postal Codes Missed Without Explicit Keywords (Recall: 88.00%)
* **What Happened**: The detector missed **6 residential PIN codes** (False Negatives).
* **Why It Failed**: In informal addresses written as `Address: Hyderabad - 500007`, the explicit keyword `PIN Code:` was omitted. To prevent clashing with GATE scores or fee amounts, my pattern required a preceding anchor, causing bare postal codes to leak in plaintext.

### Failure Case 4: Token Boundary Splits in Scanned Marksheets (OCR Artifacts)
* **What Happened**: Hard line breaks inside digit strings (e.g., `2363 5412\n8915`) broke regex boundaries, causing Verhoeff checksum validation to fail.
* **Remedy**: I added an upstream normalization step to stitch split digit sequences before running regex detection.

---

## 6. What I Would Do Differently & My Phase 2 Roadmap

### Lessons I Learned
1. **Regex Has a Hard Limit**: Deterministic rules are fast and work well for structured numbers (Aadhaar, PAN, IFSC). However, they cannot reliably extract human names or informal addresses from unstructured natural text.
2. **Mathematical Validation is Essential**: Aadhaar's Verhoeff algorithm gave 100% precision because mathematical validation eliminates guessing.

### My Plan for Phase 2 (Browser Extension Development)
1. **Hybrid Architecture**: Keep regex for checksum-backed identifiers (Aadhaar, PAN, IFSC, Mobile, Email, UPI), and add a lightweight, quantized on-device token classifier (such as an 8-bit ONNX DistilBERT or BiLSTM-CRF) to catch unanchored names in narrative essays. The model will run entirely on the user's CPU with zero network calls.
2. **Context Disambiguation**: Use dependency parsing to separate personal residential PIN codes from institutional hall tokens.
3. **Browser Extension Integration**: Package the core logic into WebAssembly (WASM) or a local Native Messaging host so users can protect prompts directly in ChatGPT, Claude, and Gemini textareas.

---
*Report submitted by M.Tech Student Researcher for Pragya Cyber × Osmania University CCoE AI Security Internship Gate 0.*
