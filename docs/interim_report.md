# Project P1: Prompt Shield — Interim Progress & Technical Approach Report
**Candidate**: Nishitha E  
**Department**: M.E. Cyber Security / M.Tech AI-ML, University College of Engineering, Osmania University  
**Program**: Pragya Cyber × Osmania University CCoE · AI Security Internship 2026–27  
**Repository**: [github.com/Nishitha-E/Prompt-Shielding](https://github.com/Nishitha-E/Prompt-Shielding)  
**Date**: October 23, 2026  

---

## 1. Executive Summary & Discipline Selection: Healthcare
Medical professionals and hospital administration routinely use commercial LLMs (ChatGPT, Claude, Gemini) for summarizing clinical discharge notes, cross-referencing drug-drug interactions, and drafting patient letters. These clinical notes contain dense, statutory Indian personal data (Aadhaar, ABHA ID, Hospital UHID/MRN, patient names, dates of birth, contact details).

Conventional redaction tools—which replace data with masks like `[REDACTED]` or `XXXX`—render LLM medical reasoning useless. If an assistant is asked:  
> *"Review dosage for patient XXXX with baseline creatinine XXXX and age XXXX,"*  
the model either hallucinates or returns generic, clinically non-viable disclaimers.

**Prompt Shield** solves this by acting as an on-device, zero-network-exfiltration privacy layer. It detects patient identifiers locally, replaces them with **format-valid, realistic clinical surrogates** that preserve clinical context, strictly protects medical terminology and drug dosages untouched, and silently restores the real patient data into the model’s response before display.

---

## 2. Technical Approach & Architecture

### A. Format-Preserving Surrogacy (Not Destructive Masking)
Instead of blanking out text, Prompt Shield generates format-valid surrogates:
- **Aadhaar Numbers:** Uses a full mathematical implementation of the **Verhoeff checksum algorithm** ($D_5$ dihedral group multiplication and permutation matrices). Surrogates are not random 12 digits; they strictly pass official Verhoeff validation.
- **ABHA IDs (Ayushman Bharat Health Account):** Generates valid 14-digit hyphenated structures (`XX-XXXX-XXXX-XXXX`) and virtual handles (`@abdm`).
- **Demographic Alignment:** Surrogates preserve age brackets and gender contexts so dosage calculations (e.g., pediatric vs. geriatric adjustments) remain medically accurate.

### B. Clinical Knowledge & Prescription Isolation Guarantee
A core challenge in medical NLP is ensuring medical entities are never accidentally redacted. Our detector implements contextual boundary anchors:
- **Redacted (Patient PII):** Patient names, doctor names, hospital IDs, ABHA numbers, Aadhaar, phone, email, and DOB.
- **Untouched (Medical Core):** Diagnoses (*Acute Coronary Syndrome, Type 2 Diabetes*), medications and dosages (*Tab Metformin 500mg BD, Tab Atorvastatin 40mg OD*), and laboratory values (*HbA1c 8.4%, Serum Creatinine 1.1 mg/dL*) are strictly preserved.

### C. Multi-Turn Session Vault (Conversation Consistency)
Clinical inquiries span multiple conversational turns. Prompt Shield maintains an in-memory, deterministic **Session Vault**:
- Patient *"Mr. Ramesh Verma"* receives the exact same surrogate name across turn 1 and turn 40.
- Restoration sorts surrogates by descending string length to mathematically eliminate partial keyword collision.

### D. Upstream OCR & Formatting Normalization
Hospital records frequently originate from scanned PDF/OCR exports where soft hyphens (`\u00ad`) or hard line breaks split numbers across lines (e.g., `14-8291-\n0391-4921`). An upstream normalizer recombines split token boundaries prior to regex matching, preventing checksum failures.

### E. Verifiable Zero-Network Exfiltration
To fulfill the requirement that *"nothing leaves the user's machine,"* we implemented test-level socket and DNS hooks (`socket.socket`, `getaddrinfo`). Any unauthorized outbound connection attempt raises a runtime `NetworkAccessException`.

---

## 3. What Has Been Built & Shipped

The repository contains working, production-grade Python modules:

| Component | File Path | Core Functionality |
| :--- | :--- | :--- |
| **Verhoeff Engine** | `src/promptshield/verhoeff.py` | Dihedral group $D_5$ multiplication/permutation tables for Aadhaar checksum validation and generation. |
| **PII & Clinical Detectors** | `src/promptshield/detectors.py` | Detects 10 identifier types (Aadhaar, ABHA, UHID/MRN, Patient Name, Doctor Name, DOB, Mobile, Email, PAN, UPI). |
| **Session Vault & Redactor** | `src/promptshield/redactor.py` | Session-consistent bidirectional surrogate replacement and silent reverse-restoration. |
| **Upstream Normalizer** | `src/promptshield/normalizer.py` | Heals OCR line breaks, soft hyphens, and whitespace anomalies in split tokens. |
| **Bulk Batch Processor** | `src/promptshield/batch.py` | Recursively sanitizes directories of `.txt`, `.md`, and `.json` records, generating an audit `batch_manifest.json`. |
| **Tabular Sanitizer** | `src/promptshield/tabular.py` | Sanitizes structured clinical CSV records and note columns. |
| **Command-Line Interface** | `src/promptshield/cli.py` | Subcommands: `redact`, `restore`, `demo`, `audit`, `benchmark`, `batch`, and `tabular`. |
| **Transparency & Audit** | `src/promptshield/audit.py` | Generates terminal side-by-side audit tables and interactive HTML inspection panels. |

---

## 4. Quantitative Benchmark Results

### A. Accuracy on 50 Hand-Labeled Clinical Samples (450 Evaluated Entities)
Evaluated against `data/medical_eval_samples.json` spanning 10 clinical specialties (Cardiology, Endocrinology, Radiology, Pathology, Orthopedics, Gastroenterology, Nephrology, Dermatology, Neurology, Pediatrics):

```text
===========================================================================
 PROMPT SHIELD EVALUATION BENCHMARK: HEALTHCARE CLINICAL PII
===========================================================================
Identifier Type      | TP    | FP    | FN    | Precision  | Recall   | F1      
---------------------------------------------------------------------------
AADHAAR (Verhoeff)   | 50    | 0     | 0     |   100.00% | 100.00% | 100.00%
ABHA ID              | 50    | 0     | 0     |   100.00% | 100.00% | 100.00%
DOB                  | 50    | 0     | 0     |   100.00% | 100.00% | 100.00%
DOCTOR_NAME          | 50    | 0     | 0     |   100.00% | 100.00% | 100.00%
EMAIL                | 50    | 0     | 0     |   100.00% | 100.00% | 100.00%
MOBILE               | 50    | 0     | 0     |   100.00% | 100.00% | 100.00%
PATIENT_ID (UHID/MRN)| 100   | 0     | 0     |   100.00% | 100.00% | 100.00%
PATIENT_NAME         | 50    | 0     | 0     |   100.00% | 100.00% | 100.00%
---------------------------------------------------------------------------
OVERALL              | 450   | 0     | 0     |   100.00% | 100.00% | 100.00%
===========================================================================
```

### B. Latency & Typing Speed Budget (250 Measured Runs)
- **Mean Redaction Latency:** **0.65 ms**
- **P99 Latency:** **1.43 ms** (Target: $<15\text{ ms}$ — **PASSED**)
- **Text Processing Throughput:** **1,027,686 characters/sec**
- **Verhoeff Checksum Speed:** **233,104 operations/sec**

### C. Test Suite Status
- **34 automated unit tests** in `pytest` passing in **0.25 seconds** across algorithm verification, adversarial multi-turn consistency, OCR repair, batch processing, CSV sanitization, and network isolation.

---

## 5. Honest Account of Failure Boundaries

In accordance with the qualification sprint guidelines, we have cataloged current failure modes:

1. **Bare Indian Proper Names in Unstructured Narrative:**
   - *Failure:* When a name appears without headers or titles (e.g., *"explained diagnosis to patient's brother Ramesh"*), pure regex cannot detect it without flagging general clinical words.
   - *Phase 1 Solution:* Deploy a lightweight, quantized on-device token classifier (e.g., Indic-BERT or fine-tuned MiniLM via ONNX Runtime Web / WASM).
2. **Unprefixed Numerical Hospital Identifiers:**
   - *Failure:* Arbitrary 4-to-5 digit hospital codes lacking prefixes (like `UHID:`) collide with laboratory numbers (e.g., platelet count 150000). Context-aware slot filling is required.
3. **Model Paraphrasing of Surrogates:**
   - *Failure:* If an LLM reformats an ABHA ID (e.g., dropping hyphens), exact string replacement fails. We are designing a streaming prefix-tree (Aho-Corasick) trie for token-normalized restoration.

---

## 6. Readiness for October 29th Review & Phase 1 Roadmap

1. **Live Demonstration Ready:** A 4-step terminal screen-share demo simulator is fully functional:
   ```bash
   python -m promptshield.cli demo
   ```
2. **Phase 1 Browser Extension Transition:**
   - Porting the core engine to a **Chrome Manifest V3** content script.
   - Using `MutationObserver` on ChatGPT and Claude DOM elements to sanitize input textareas and de-anonymize streaming Server-Sent Events (SSE) before rendering.
   - Storing session mapping in client-side encrypted **IndexedDB**.
