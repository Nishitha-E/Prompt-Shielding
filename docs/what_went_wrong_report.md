# Gate 0 Progress & Technical Failure Report: What Was Done & What Went Wrong

**Project Title**: Prompt Shield — Indian PII Protection for AI Prompts  
**Domain**: Education Sector (Admissions, Scholarships, Student Enquiries)  
**Dataset Reference**: [Indic Synthetic Profiles](https://huggingface.co/datasets/adwaith06/indic-synthetic-profiles) (Hugging Face: `adwaith06/indic-synthetic-profiles`)  
**Program**: Pragya Cyber × Osmania University CCoE · AI Security Internship 2026–27  
**Author**: M.Tech Student Researcher  
**Repository**: [https://github.com/Nishitha-E/Prompt-Shielding](https://github.com/Nishitha-E/Prompt-Shielding)  
**Date**: October 2026  

---

## 1. Project Background & Dataset Selection

Public Large Language Models (ChatGPT, Claude, Gemini) are increasingly used by students and applicants to draft admission essays, review scholarship applications, and resolve fee inquiries. These prompts frequently contain sensitive personal identifiers. 

Instead of simple irreversible redaction (e.g., replacing names with `[REDACTED]`), **Prompt Shield** replaces sensitive Indian identifiers with realistic, format-valid synthetic surrogates, maintains a local session vault, and silently restores the original values when the AI response returns.

### Dataset Reference
We selected the open-source **Indic Synthetic Profiles** dataset (`adwaith06/indic-synthetic-profiles`), available on Hugging Face under the MIT license. It provides 10,000 synthetic Indian profile records covering 8 Indian languages, native scripts, contact details, identification numbers, and academic fields. Because the dataset consists of structured tabular records, we extracted realistic profile patterns to synthesize natural-language academic prompts and manually established ground-truth spans for evaluation.

---

## 2. What Has Been Done So Far (Implementation Progress)

Across the qualification sprint, work was carried out in progressive stages and committed over 11 distinct days on Git:

### A. Mathematical Checksum Implementation (`src/promptshield/verhoeff.py`)
- Implemented the **Verhoeff checksum algorithm** using the dihedral group $D_5$ multiplication table (`VERHOEFF_D`), permutation table (`VERHOEFF_P`), and inverse table (`VERHOEFF_INV`).
- Enables mathematically sound validation of 12-digit Indian Aadhaar numbers to reject arbitrary numerical strings.
- Implemented `generate_verhoeff_number()` to generate format-valid synthetic Aadhaar surrogates that pass external validation.

### B. Core Indian PII Detectors & Surrogate Generators (`src/promptshield/detectors.py`)
Implemented deterministic recognizers and realistic surrogate generators for the core **Indian identifier types**:
1. **Aadhaar**: 12-digit format with Verhoeff validation and checksum-valid synthetic surrogates.
2. **PAN Card**: Standard 10-character alphanumeric structure (`[A-Z]{5}[0-9]{4}[A-Z]`).
3. **Indian Mobile**: 10-digit mobile numbers starting with 6–9, supporting `+91` international prefixes.
4. **Email Address**: Standard RFC format with common personal domains.
5. **IFSC Code**: 11-character bank branch identifier (`[A-Z]{4}0[A-Z0-9]{6}`).
6. **Bank Account Number**: 9 to 18 digit account numbers with contextual keywords.
7. **UPI ID**: Virtual Payment Addresses with Indian bank and PSP handles (`@oksbi`, `@okhdfcbank`, `@paytm`, `@ybl`).
8. **Postal PIN Code**: 6-digit Indian postal codes (100000–899999).
9. **Person / Student Name**: Extraction via contextual headers (`Name:`, `Student Name:`, `Applicant:`) and Indian salutations (`Mr.`, `Ms.`, `Kumar`, `Kumari`).

Academic context fields such as student roll numbers, college names, degrees, marks, and GATE scores are preserved unchanged.

### C. Reversible Session Engine & Academic Context Preservation (`src/promptshield/redactor.py`)
- **Session Consistency**: Ensures that if an original identifier appears multiple times in a conversation, it receives the exact same synthetic surrogate.
- **Local Vault**: Mappings are stored strictly in memory or exported to a local session JSON file. No personal data leaves the user's computer.
- **Silent Reverse Restoration**: When the LLM generates a response referencing the synthetic surrogate, the engine restores the user's real data. Replacements are ordered by surrogate length in descending order to prevent substring collisions.
- **Academic Context Preservation**: Built specifically to leave university names (*Osmania University*), degree programs (*M.E. Cyber Security*), CGPA (*8.85 / 10.0*), GATE scores (*680*), and scholarship fee amounts untouched.

### D. Command-Line Interface (`src/promptshield/cli.py`)
Built a clean, straightforward student CLI supporting 4 subcommands:
```bash
# 1. Mask PII in a prompt and save session
python -m promptshield.cli redact -i prompt.txt -o masked.txt -s session.json

# 2. Restore original values in model response
python -m promptshield.cli restore -i model_response.txt -o final.txt -s session.json

# 3. Live 4-step demonstration
python -m promptshield.cli demo

# 4. Automated 50-sample evaluation benchmark
python -m promptshield.cli eval
```

### E. 50 Hand-Labeled Evaluation Samples (`data/education_eval_samples.json`)
Generated and hand-annotated 50 synthetic evaluation records across 10 academic scenarios (PG admissions, ePASS scholarships, hostel booking, hall tickets, placement drives, loan verification, transcripts, fee receipts, library clearance, and re-evaluation).

### F. Automated Test Suite (`tests/`)
Created 18 automated unit tests across 3 clean test modules (`test_verhoeff.py`, `test_detectors.py`, `test_redactor.py`). All 18 tests execute and pass in under 0.15 seconds.

---

## 3. Empirical Evaluation Benchmark

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

Overall metrics across 466 evaluated entities:
- **Precision**: **98.20%**
- **Recall**: **93.56%**
- **F1 Score**: **95.82%**
- **Total Errors**: **38** (8 False Positives, 30 False Negatives).

---

## 4. What Went Wrong: Root Cause Failure Analysis

Rather than claiming unrealistic 100% perfection, we conducted an in-depth boundary failure analysis:

### Failure Mode 1: Severe Recall Drop on Unanchored Names (Recall: 63.64%)
* **The Error**: Missed **24 out of 66 personal names** (False Negatives).
* **Root Cause**: Regular expressions rely on contextual anchors (`Student Name:`) or salutations (`Mr./Ms.`). When students wrote narrative statements such as *"I discussed my admission with my guardian Suresh Reddy"* or *"I, Ananya Verma, submit this form"*, the names were completely overlooked.
* **Why regex cannot fix this**: Matching any two capitalized words (`[A-Z][a-z]+ [A-Z][a-z]+`) produces disastrous false positives by redacting `Osmania University`, `Cyber Security`, `State Government`, etc.

### Failure Mode 2: Over-Redaction of Campus Venue Codes as PIN Codes (Precision: 84.62%)
* **The Error**: **8 False Positives** on PIN codes.
* **Root Cause**: 6-digit campus venue terminals, hall codes, or fee counter tokens (e.g., `Venue PIN Code: 500045`) matched the 6-digit postal pattern. This removes non-sensitive location context, degrading the LLM's assistance.

### Failure Mode 3: Missing Context Anchors on Inline Postal Codes (Recall: 88.00%)
* **The Error**: Missed **6 postal PIN codes** (False Negatives).
* **Root Cause**: When students wrote addresses informally without the explicit phrase `PIN Code:` (e.g., `Address: Near Tarnaka, Hyderabad - 500007`), the detector ignored the number to prevent clashing with GATE scores or fee sums.

### Failure Mode 4: Token Boundary Degradation from OCR and Scanned Marksheets
* **The Error**: Scanned documents and PDF exports introduce hard line breaks inside digit sequences (e.g., `1005-26-\n749` or `2363 5412\n8915`).
* **Root Cause**: Regex patterns operate across single lines by default. While basic string normalization repairs isolated 4-digit splits, OCR artifacts with soft hyphens (`\u00ad`) or zero-width spaces break regex match boundaries.

---

## 5. Engineering Retrospective & Phase 2 Roadmap

### Lessons Learned
1. **Deterministic Rules Have Limits**: Regex is ideal for mathematically validated identifiers (Aadhaar with Verhoeff, PAN, IFSC). However, unstructured names and addresses in narrative text require semantic models.
2. **Mathematical Checksums are Invaluable**: Aadhaar's Verhoeff algorithm achieved 100% precision without needing contextual keywords, proving the value of checksum validation.
3. **Local Latency Advantage**: The regex engine processes prompts in under 0.1 ms, easily meeting the requirement that typing in the UI never feels delayed.

### Phase 2 Architecture (Browser Extension)
1. **Hybrid Detection**: Retain regex for checksum identifiers; integrate a lightweight on-device token classifier (8-bit quantized DistilBERT or BiLSTM-CRF via ONNX Runtime Web) running locally in the browser to detect unanchored names in narrative paragraphs.
2. **Context Disambiguation**: Use dependency parsing to separate personal postal PINs from institutional hall numbers and transaction IDs.
3. **Manifest V3 Extension**: Package the engine as a browser extension to intercept prompt submissions directly in ChatGPT, Claude, and Gemini textareas.

---
*Report submitted for the Pragya Cyber × Osmania University CCoE AI Security Internship Gate 0.*
