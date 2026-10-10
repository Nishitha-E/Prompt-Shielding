# Prompt Shield: Failure Modes & Boundary Analysis Report

As part of the **P1 Qualification Sprint** criteria, this report provides an honest account of current failure modes, edge cases, and limitations of the rule-based / regex detection approach on Indian Healthcare & Clinical datasets.

---

## Failure Case 1: Indian Names in Free Narrative Clinical Text
* **Example Scenario**:
  > *"Prognosis explained to patient's brother Ramesh and daughter Sunita in ICU waiting area."*
* **Observed Behavior**:
  The detector missed both `Ramesh` and `Sunita`.
* **Root Cause & Why It Fails**:
  In clinical notes, names frequently appear inside unstructured doctor's narrative progress notes without formal headers (e.g., without `Patient Name:`) or salutations (`Mr./Mrs./Dr.`). 
  Because regex rules rely on structural anchors or honorifics, detecting bare proper nouns requires semantic Named Entity Recognition (NER) models (such as Clinical Indic-BERT or fine-tuned Transformer token classifiers). Pure regex dictionaries for Indian names cause unacceptable false positives when words share spelling with non-PII terms or medical jargon.
* **Path to Resolution (Phase 1 & 2)**:
  Integrate a quantized on-device token classifier (via ONNX Runtime Web / Transformers.js) running locally in the browser/CLI to identify PERSON entities in free-form narrative contexts without network transmission.

---

## Failure Case 2: Numerical Ambiguity Between Short Hospital IDs and Clinical Lab Values
* **Example Scenario**:
  > *"Patient admitted under 40291. Vital signs: Pulse 78 bpm, Platelets 150000/mcL, Glucose 140 mg/dL."*
* **Observed Behavior**:
  If the `UHID:` or `MRN:` prefix is missing from `40291`, the detector fails to flag it to avoid false-positive flagging of clinical lab counts. Conversely, aggressive 5-digit number matching risks redacting physiological readings.
* **Root Cause & Why It Fails**:
  Unlike Aadhaar numbers (which have 12 digits and a strict Verhoeff mathematical checksum), local hospital patient record numbers (MRN/UHID) have arbitrary length (4 to 8 digits) and no standardized checksum algorithm across different hospital management software (HMS).
* **Path to Resolution (Phase 1 & 2)**:
  Implement slot-filling heuristic parsing: extract key-value pairs from clinical header blocks and build hospital-specific HMS template adapters.

---

## Failure Case 3: Broken Token Boundaries from OCR / Markdown Formatting
* **Example Scenario**:
  > Scanned discharge summary exported via OCR:
  > ```text
  > ABHA ID: 14-8291-
  > 0391-4921 | Aadhaar: 2363 5412
  > 8915
  > ```
* **Observed Behavior**:
  The line break separates the 14-digit ABHA and 12-digit Aadhaar into two disconnected segments. The Verhoeff checksum validator fails because the captured token is incomplete (`2363 5412` is only 8 digits).
* **Root Cause & Why It Fails**:
  Regex pattern matching operates sequentially line-by-line or token-by-token. Hard line breaks introduced by fixed-width formatting or OCR scanning break regex boundaries.
* **Path to Resolution (Phase 1 & 2)**:
  Add an upstream text normalization pre-processing pipeline that strips soft line breaks within digit sequences before feeding text into `PIIDetector`.
