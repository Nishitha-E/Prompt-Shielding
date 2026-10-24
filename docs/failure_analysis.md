# Prompt Shield: Failure Modes & Boundary Analysis Report
**Domain**: Education Sector (Admissions, Scholarships, Student Enquiries)  
**Dataset Reference**: [Indic Synthetic Profiles (Hugging Face: adwaith06/indic-synthetic-profiles)](https://huggingface.co/datasets/adwaith06/indic-synthetic-profiles)  
**Program**: Pragya Cyber × Osmania University CCoE · AI Security Internship 2026–27  

As part of the **P1 Qualification Sprint** criteria, this report provides an honest account of current failure modes, edge cases, and limitations of the rule-based / regex detection approach on Indian Education datasets.

---

## Failure Case 1: Indian Names in Free Narrative Statement of Purpose (SOP) Essays
* **Example Scenario**:
  > *"I completed my final year project under guidance of my senior batchmates Rahul and Ananya at Osmania University."*
* **Observed Behavior**:
  The detector missed both `Rahul` and `Ananya`.
* **Root Cause & Why It Fails**:
  In admission essays and student correspondence, personal names often appear inside free-form narrative paragraphs without structured headers (such as `Student Name:`) or formal honorifics (`Mr./Ms.`).
  Because regex rules rely on contextual anchors or salutations, detecting bare proper nouns requires semantic Named Entity Recognition (NER) models (such as Indic-BERT or fine-tuned Transformer token classifiers). Pure dictionary matching for Indian names produces unacceptable false positives when words share spelling with common nouns or technical terms.
* **Path to Resolution (Phase 1 & 2)**:
  Integrate a quantized on-device token classifier (via ONNX Runtime Web / Transformers.js) running locally in the browser/CLI to identify PERSON entities in free-form narrative contexts without network transmission.

---

## Failure Case 2: Numerical Ambiguity Between PIN Codes, Fee Amounts, and Roll Numbers
* **Example Scenario**:
  > *"Paid admission challan 500007 for registration 100526. Rank 50002."*
* **Observed Behavior**:
  If context prefixes like `PIN Code:`, `Roll No:`, or `Fee:` are omitted, arbitrary 6-digit numbers (`500007`) are ambiguous—they could be a postal PIN code (Hyderabad GPO: 500007), a student registration number, or an exam rank. Overly aggressive 6-digit pattern matching risks redacting academic ranks or fee figures.
* **Root Cause & Why It Fails**:
  Unlike 12-digit Aadhaar numbers (which have a strict mathematical Verhoeff checksum), postal PIN codes, ranks, and roll numbers often share 6-digit lengths with no universal internal checksum.
* **Path to Resolution (Phase 1 & 2)**:
  Implement slot-filling heuristic parsing: extract key-value pairs from structured student application blocks and build university-specific HMS/ERP template adapters.

---

## Failure Case 3: Broken Token Boundaries from OCR / PDF Formatting in Scanned Marksheets
* **Example Scenario**:
  > Scanned bonafide or marksheet exported via OCR:
  > ```text
  > Roll No: 1005-26-
  > 749 | Aadhaar: 2363 5412
  > 8915
  > ```
* **Observed Behavior**:
  The line break separates the 12-digit Aadhaar into two disconnected segments (`2363 5412` and `8915`). The Verhoeff checksum validator fails because the captured token is incomplete.
* **Root Cause & Why It Fails**:
  Regex pattern matching operates sequentially line-by-line or token-by-token. Hard line breaks introduced by fixed-width columns or OCR scanning break regex boundaries.
* **Path to Resolution (Phase 1 & 2)**:
  Our upstream normalizer (`src/promptshield/normalizer.py`) recombines split digit sequences before regex detection.
