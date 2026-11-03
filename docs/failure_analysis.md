# Prompt Shield: Failure Modes & Boundary Analysis Report

**Project Title**: Prompt Shield: Privacy-Preserving Indian PII Substitution for AI Prompts  
**Domain**: AI Security, Privacy-Enhancing Technologies (PETs), Education Sector Track  
**Program**: Pragya Cyber × Osmania University CCoE · AI Security Internship 2026–27  
**Author / Candidate**: M.Tech Student Researcher  
**Dataset Reference**: Indic Synthetic Profiles (`adwaith06/indic-synthetic-profiles` on Hugging Face, MIT License)  

---

## 1. Executive Summary & Evaluation Context

Claiming 100% precision and recall in natural-language PII detection is unrealistic. Real-world student prompts feature conversational grammar, informal abbreviations, unanchored proper nouns, and ambiguous numerical sequences that deterministic regular expressions cannot fully resolve.

Prompt Shield was evaluated against **50 ground-truth annotated synthetic education records** directly extracted from the official MIT-licensed `indic-synthetic-profiles` dataset. Across 466 evaluated entities, the system achieved:
* **Precision**: **98.20%**
* **Recall**: **93.56%**
* **F1 Score**: **95.82%**
* **Total Documented Errors**: **38** (8 False Positives, 30 False Negatives)

---

## 2. Failure Case 1: Unanchored Names in Free-Form Narrative (Recall: 63.64%)

### The Problem:
In natural student correspondence and Statement of Purpose (SOP) essays, students mention names inside conversational sentences:
> *"I discussed my admission with my guardian Suresh Reddy."*  
> *"My name is Nancy Wheeler and I secured state rank 10."*

### Root Cause & Why Regex Fails:
* Deterministic regex relies on explicit structural anchors (such as `Student Name:`, `Applicant:`) or formal honorific salutations (`Mr.`, `Ms.`, `Kumar`, `Kumari`).
* When names appear in free-form narrative prose without a title or colon, regex rules ignore them, causing **24 False Negatives**.
* **Why regex cannot fix this**: If we relax the pattern to match arbitrary capitalized word pairs (`[A-Z][a-z]+ [A-Z][a-z]+`), it creates severe false positives by destroying non-sensitive educational context like `Osmania University`, `Cyber Security`, `State Government`, and `Advanced Cryptography`.

### Phase 2 Resolution:
Integrate a lightweight, on-device Machine Learning token classifier (such as an 8-bit quantized DistilBERT or BiLSTM-CRF via ONNX Runtime Web) running locally in the browser to recognize names from sentence context without network transmission.

---

## 3. Failure Case 2: Ambiguous 6-Digit Campus Codes Flagged as PIN Codes (Precision: 84.62%)

### The Problem:
In academic correspondence, 6-digit numbers frequently designate campus test venue codes, exam hall tokens, or bank fee counters (e.g., `Venue PIN Code: 500045`).

### Root Cause & Why Regex Fails:
* Unlike 12-digit Aadhaar numbers (which have a strict mathematical Verhoeff checksum), postal PIN codes, ranks, and exam terminal IDs share identical 6-digit lengths with no internal checksum.
* The detector's pattern `(?:PIN(?:\s*Code)?|Postal\s*Code)[\s.:#-]+([1-9][0-9]{5})` triggered on these public codes, producing **8 False Positives**.
* While redacting a public hall code does not leak privacy, it removes non-sensitive location context, causing the AI assistant to give confused directions.

### Phase 2 Resolution:
Implement dependency slot-filling to distinguish personal residential addresses from institutional venue tokens.

---

## 4. Failure Case 3: Inline Postal Codes Missed Without Explicit Keywords (Recall: 88.00%)

### The Problem:
When students write addresses informally without the explicit phrase `PIN Code:` (e.g., `Address: Near Tarnaka, Hyderabad - 500007`), the detector missed the postal PIN code (**6 False Negatives**).

### Root Cause & Why Regex Fails:
To prevent false alarms on marks, ranks (like rank 10), or fee sums (like 50000), the regex pattern enforces an anchor keyword (`PIN Code:`), causing bare inline postal codes to be skipped.

### Phase 2 Resolution:
Use token-level location contextual parsing to recognize 6-digit numbers following known Indian city and state names.

---

## 5. Summary Table of Empirical Errors

```text
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
