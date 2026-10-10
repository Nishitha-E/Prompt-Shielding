# Prompt Shield: Gate 0 Technical Note
**Applicant**: Nishitha-E  
**Project**: P1 Prompt Shield (Healthcare & Clinical Data Track)  
**Program**: Pragya Cyber × Osmania University CCoE · AI Security Internship 2026–27  

---

## 1. What Was Built

Prompt Shield is a local, privacy-preserving security intermediary engineered to protect sensitive Indian personal and healthcare identifiers before prompts are dispatched to commercial LLMs (ChatGPT, Claude, Gemini). Unlike conventional redaction tools that replace sensitive data with destructive masks (e.g. `[REDACTED]` or `XXXX`), which render model responses incoherent or clinically unhelpful, Prompt Shield implements a bidirectional surrogate architecture:

1. **Multi-Category On-Device Detector**:
   - Indian National Identifiers: 12-digit Aadhaar with real mathematical **Verhoeff algorithm** checksum verification ($D_5$ dihedral group multiplication/permutation tables), PAN card (`[A-Z]{5}[0-9]{4}[A-Z]`), Indian mobile numbers (`+91` variations), UPI VPAs (`@okhdfcbank`, `@ybl`, etc.), and IFSC codes.
   - Healthcare Clinical Identifiers: 14-digit ABHA IDs (`XX-XXXX-XXXX-XXXX`), ABHA virtual addresses (`@abdm`), Hospital Patient IDs/MRN/UHID (`UHID: 984721`), Patient & Doctor names with clinical context anchors, and Date of Birth.
   - **Clinical Preservation Guarantee**: Clinical terminology, medications, dosages (`Metformin 500mg`), and lab parameters (`HbA1c 8.4%`) are strictly isolated and preserved so the model's medical reasoning remains unimpaired.
2. **Format-Valid Surrogate Generation**:
   - Generates synthetic replacements that mirror the exact format, length, and validation checksums of the original identifiers (e.g., surrogate Aadhaar numbers strictly satisfy the Verhoeff checksum algorithm).
3. **Session-Consistent Vault & Reverse Restoration**:
   - A deterministic session mapping table guarantees that an identifier receives the exact same surrogate across arbitrary conversational turns (verified up to 40 turns), and silently reverses the surrogates in the assistant's output back to original patient values.
4. **CLI & Audit Subsystem**:
   - Complete command-line interface supporting `redact`, `restore`, an interactive live `demo` harness for screen-share evaluation, and an interactive HTML transparency panel.
5. **Evaluation Benchmark**:
   - 50 hand-labeled synthetic clinical records evaluating detection precision and recall across 10 medical disciplines, backed by an automated evaluation pipeline (`src/promptshield/evaluate.py`).

---

## 2. What I Would Do Differently

Reflecting on the initial design and the empirical failure modes identified during evaluation:

1. **Hybrid Architecture (Regex Rules + Local SLM/NER) Over Pure Pattern Matching**:
   - While regex matching is fast and deterministic for structured tokens (Aadhaar, PAN, ABHA), it struggles with Indian proper names in free-form narrative doctor notes lacking honorifics or headers (e.g., *"Explained condition to brother Ramesh"*).
   - In hindsight, a dual-layer approach would be superior: fast pattern filters for structured checksums, combined with a lightweight, quantized on-device token classifier (e.g., Indic-BERT or fine-tuned RoBERTa running via ONNX Runtime Web) for unstructured narrative entities.
2. **Context-Aware Numerical Disambiguation**:
   - Unprefixed 4-to-6 digit patient IDs present a collision risk with clinical quantities (e.g., platelet counts or blood pressure readings). Relying on keyword prefixes (`UHID:`, `MRN:`) prevented false positives, but missed unprefixed registration codes. Implementing slot-filling dependency parsers would enable context-aware boundary detection without prefix dependency.
3. **Token Normalization Prior to Regex Application**:
   - Line breaks and OCR hyphenation artifacts in digitized medical documents split contiguous digit sequences, breaking checksum evaluation. An upstream normalizer should have been implemented from day one.

---

## 3. What Would Be Needed to Make It Work at Scale

Transitioning Prompt Shield from a CLI prototype to a production-grade browser extension deployed across thousands of healthcare and legal professionals requires four critical architectural pillars:

### A. Manifest V3 Browser Extension Architecture
- **In-DOM Interceptor**: Content script hooking into `<textarea>` and contenteditable DOM elements on ChatGPT (`chatgpt.com`), Claude (`claude.ai`), and Gemini (`gemini.google.com`).
- **Input Pipeline**: Intercept the dispatch event on the submit button, run local redaction synchronously in under 15 milliseconds, update the input buffer with surrogates, and allow transmission.
- **Output Observer**: A `MutationObserver` listening to incoming streaming response chunks from the LLM, silently substituting surrogates back to original clinical values before DOM rendering.

### B. Client-Side On-Device Inference (Zero Network Exfiltration)
- Deployment of models directly into the browser execution sandbox using **ONNX Runtime Web** (WebAssembly / WebGPU backend) and **Transformers.js**.
- Strict Content Security Policy (CSP) headers ensuring that zero network calls leave the extension for detection or mapping purposes. All mapping states remain strictly inside local browser memory.

### C. Persistent Session Vault via IndexedDB
- Replace file-based JSON session mappings with an encrypted client-side **IndexedDB** database keyed by conversation URL or session ID.
- Enable automatic TTL expiration and secure memory wipes when the user closes their browser tab or clears conversation history.

### D. Streaming Token De-Anonymization
- In production, LLMs stream tokens incrementally via Server-Sent Events (SSE). Reversing multi-token surrogates (e.g. `14-8291-0391-4921`) requires a streaming Aho-Corasick or prefix-tree trie buffer that matches and replaces surrogates across partial token boundaries without buffering entire model outputs.
