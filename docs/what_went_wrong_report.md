# Gate 0 Formal Retrospective & Failure Report: What Went Wrong
**Project Title**: Prompt Shield — Indian PII Protection for AI Prompts  
**Domain**: Education Sector (Admissions, Scholarships, Student Enquiries)  
**Dataset Reference**: [Indic Synthetic Profiles](https://huggingface.co/datasets/adwaith06/indic-synthetic-profiles) (Hugging Face: adwaith06/indic-synthetic-profiles)  
**Program**: Pragya Cyber × Osmania University CCoE · AI Security Internship 2026–27  
**Author**: M.Tech Student Researcher  
**Date**: October 2026  

---

## 1. Executive Summary & Benchmark Results

As specified in the **Pragya Cyber × Osmania University CCoE Internship Project Brief**, claiming 100% precision and recall is treated with immediate suspicion because real-world natural language PII detection inevitably encounters edge cases, false alarms, and missed detections.

In this qualification sprint, Prompt Shield was evaluated against **50 hand-labeled, ground-truth annotated synthetic education records** derived from the MIT-licensed `adwaith06/indic-synthetic-profiles` dataset. These records encompass 10 realistic university workflows: PG admissions, state ePASS scholarship applications, campus hostel allotments, duplicate hall ticket issuance, campus placement resumes, bank education loan verification, official transcript requests, tuition fee UPI receipts, library clearance, and examination recounting requests.

### Empirical Performance Summary

```
Identifier       TP    FP    FN    Precision  Recall   F1      
AADHAAR          50    0     0       100.00% 100.00% 100.00%
BANK_ACCOUNT     50    0     0       100.00% 100.00% 100.00%
DOB              50    0     0       100.00% 100.00% 100.00%
EMAIL            50    0     0       100.00% 100.00% 100.00%
IFSC             50    0     0       100.00% 100.00% 100.00%
MOBILE           50    0     0       100.00% 100.00% 100.00%
PAN              50    0     0       100.00% 100.00% 100.00%
PINCODE          44    8     6        84.62%  88.00%  86.27%
STUDENT_ID       100   0     0       100.00% 100.00% 100.00%
STUDENT_NAME     42    0     24      100.00%  63.64%  77.78%
UPI              50    0     0       100.00% 100.00% 100.00%
-----------------------------------------------------------------
OVERALL          586   8     30       98.65%  95.13%  96.86%
```

The system achieved **98.65% Precision**, **95.13% Recall**, and **96.86% F1-score**. The errors were deliberately not hidden: **30 False Negatives (missed PII)** and **8 False Positives (over-redacted non-PII)** occurred. The following sections detail why these failures occurred and what must be done to resolve them.

---

## 2. What Went Wrong: Root Cause Analysis

### Failure Mode 1: Severe Recall Drop on Unanchored Student & Guardian Names (Recall: 63.64%)
* **Observed Flaw**: The system missed **24 out of 66 personal names** in the test set.
* **Why it Failed**:
  - The deterministic regular expression relies on structural cues such as `Student Name:`, `Applicant:`, or honorific salutations (`Mr.`, `Ms.`, `Kumar`, `Kumari`).
  - In real-world Statements of Purpose (SOP) and narrative inquiries, students write sentences like:
    > *"I discussed my admission options with my guardian Suresh Reddy."*  
    > *"I, Ananya Verma, submit that my semester fees were paid on time."*
  - Because `Suresh Reddy` and `Ananya Verma` in narrative context lack a formal `Name:` anchor or honorific prefix, the regex engine completely overlooked them.
  - Attempting to match bare capitalized bigrams (`[A-Z][a-z]+ [A-Z][a-z]+`) in natural text immediately causes catastrophic false positives by redacting educational context like `Osmania University`, `Cyber Security`, `State Government`, and `Advanced Cryptography`.

### Failure Mode 2: False Positive Ingestion of 6-Digit Institutional Codes as PIN Codes (Precision: 84.62%)
* **Observed Flaw**: The system generated **8 False Positives** on PIN codes.
* **Why it Failed**:
  - In university applications, students frequently cite institutional reference numbers that share the 6-digit postal code syntax (e.g., `Venue PIN Code: 500045`, fee payment counter numbers, or regional exam sub-center tokens).
  - The detector's pattern `(?:PIN(?:\s*Code)?|Postal\s*Code)[\s.:#-]+([1-9][0-9]{5})` triggered on these public venue and terminal numbers.
  - While redacting a public exam center code does not leak personal data, it corrupts the academic context given to the LLM assistant, leading the model to hallucinate or generate confused instructions regarding test locations.

### Failure Mode 3: Missing Context Anchors on Inline Postal Codes (Recall: 88.00%)
* **Observed Flaw**: In **6 samples**, the student's residential PIN code was completely missed (False Negative).
* **Why it Failed**:
  - When students wrote their address in informal inline format (e.g., `Address: Near Tarnaka, Hyderabad - 500007`), the strict anchor `PIN Code:` was absent.
  - Without the keyword, the regex engine ignored the 6-digit number to avoid false-matching GATE scores or fee amounts. Consequently, the user's postal PIN was leaked in raw text.

### Failure Mode 4: Format Variations and Token Boundary Disruptions
* **Observed Flaw**: Rigid boundary assumptions fail when text is exported from PDFs or OCR scans.
* **Why it Failed**:
  - Scanned admission bonafides and marksheets frequently introduce hard line breaks inside continuous digit streams (e.g., `1005-26-\n749` or `2363 5412\n8915`).
  - While our basic in-memory normalizer fixed isolated 4-digit breaks, it relies on greedy regex replacement that can fail when non-breaking whitespace (`\u00a0`), zero-width spaces (`\u200b`), or soft hyphens (`\u00ad`) appear unpredictably.

---

## 3. Engineering Retrospective: What Would We Do Differently?

1. **Rule-Based Regex is Insufficient for Unstructured Text**:
   Regex excels at syntactically rigid identifiers with mathematical checksums (Aadhaar with Verhoeff, PAN with fixed character positions, IFSC with 4-letter prefixes). However, natural-language personal names and addresses cannot be solved through regular expressions alone. Regex will always force an unacceptable trade-off between missing names (low recall) or destroying non-sensitive text (low precision).

2. **The Power of Mathematical Checksum Verification**:
   The Aadhaar implementation proved that mathematical validation (Verhoeff dihedral group $D_5$) provides 100% precision. Even if a 12-digit student registration number or serial number appears in a prompt, the Verhoeff checksum instantly discriminates between a genuine Aadhaar number and an arbitrary 12-digit number without needing contextual keywords.

3. **Session Vault Overlap Collisions**:
   During reverse restoration, if a surrogate is a substring of another word or if two surrogates share prefixes, naive `.replace()` calls can cause corruptions. We mitigated this by sorting replacements in descending order of string length, but a trie-based or token-index-based replacement mechanism is required for enterprise scale.

---

## 4. Phase 2 Scale & Architectural Roadmap

To eliminate the 30 false negatives and 8 false positives before deploying the browser extension, the following architecture will be implemented:

```
                          Incoming Student Prompt
                                     │
                                     ▼
                     ┌───────────────────────────────┐
                     │   Stage 1: Upstream Cleaner   │  (Heal OCR splits & Unicode)
                     └───────────────┬───────────────┘
                                     │
                ┌────────────────────┴────────────────────┐
                ▼                                         ▼
   ┌───────────────────────────┐             ┌───────────────────────────┐
   │ Fast Deterministic Engine │             │ Local On-Device Small NER │
   │ (Verhoeff Aadhaar, PAN,   │             │ (DistilBERT / BiLSTM-CRF  │
   │  IFSC, Mobile, Email, UPI)│             │  for Free-Form Names &    │
   │ Latency: < 0.1 ms         │             │  Addresses in Narrative)  │
   └────────────┬──────────────┘             └─────────────┬─────────────┘
                │                                         │
                └────────────────────┬────────────────────┘
                                     ▼
                     ┌───────────────────────────────┐
                     │   Stage 3: Local Vault &      │  (Format-valid synthetic
                     │   Surrogate Generator         │   substitution + Session map)
                     └───────────────┬───────────────┘
                                     │
                                     ▼
                         Sanitized Outgoing Prompt
```

1. **Hybrid Architecture (Regex + Lightweight Local NER)**:
   - Retain regex for checksum-backed identifiers (Aadhaar, PAN, IFSC, UPI, Phone).
   - Introduce an on-device, quantized token classifier (e.g., 8-bit quantized MobileBERT or BiLSTM-CRF via ONNX Runtime Web). This model will run completely on the user's CPU without sending a single byte to any external server.
2. **Context-Aware Disambiguation**:
   - Classify 6-digit numbers based on preceding dependency trees (differentiating postal codes from marks, ranks, or venue receipts).
3. **Browser Extension Manifest V3 Integration**:
   - Package the Python logic into WebAssembly (WASM) or a local Native Messaging host to intercept prompt submissions directly in ChatGPT, Claude, and Gemini textareas.

---
*Report completed for the Pragya Cyber × Osmania University CCoE AI Security Internship Gate 0 submission.*
