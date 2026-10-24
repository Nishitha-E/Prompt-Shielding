# Prompt Shield: Gate 0 Technical Note
**Applicant**: Nishitha-E  
**Project**: P1 Prompt Shield (Education Sector Track)  
**Dataset Reference**: [Indic Synthetic Profiles (Hugging Face: adwaith06/indic-synthetic-profiles)](https://huggingface.co/datasets/adwaith06/indic-synthetic-profiles)  
**Program**: Pragya Cyber × Osmania University CCoE · AI Security Internship 2026–27  

---

## 1. What Was Built

Prompt Shield is a local, privacy-preserving security intermediary engineered to protect sensitive Indian personal and student identifiers before prompts are dispatched to commercial LLMs (ChatGPT, Claude, Gemini). Unlike conventional redaction tools that replace sensitive data with destructive masks (e.g. `[REDACTED]` or `XXXX`), which render model responses incoherent or academically unhelpful, Prompt Shield implements a bidirectional surrogate architecture:

1. **Multi-Category On-Device Detector**:
   - Statutory Indian Identifiers: 12-digit Aadhaar with real mathematical **Verhoeff algorithm** checksum verification ($D_5$ dihedral group multiplication/permutation tables), PAN card (`[A-Z]{5}[0-9]{4}[A-Z]`), Indian mobile numbers (`+91` variations), UPI VPAs (`@okhdfcbank`, `@oksbi`, etc.), and IFSC codes.
   - Education & Student Identifiers: Bank Account Numbers, Postal PIN Codes, Student Roll/Application IDs (`Roll No: 1005-26-701`, `App No: OU26-49102`), Student Names with header/honorific anchors, and Date of Birth.
   - **Academic Preservation Guarantee**: College names (*University College of Engineering, Osmania University*), degree programs (*M.E. Cyber Security, B.Tech CSE*), GATE scores, CGPA (*8.85 / 10.0*), and scholarship fee amounts (*Rs. 35,000*) are strictly isolated and preserved so the model's educational reasoning remains unimpaired.
2. **Format-Valid Surrogate Generation**:
   - Generates synthetic replacements modeled on the schema of the **Indic Synthetic Profiles** dataset, preserving exact format, length, and validation checksums (e.g., surrogate Aadhaar numbers strictly satisfy the Verhoeff checksum algorithm).
3. **Session-Consistent Vault & Reverse Restoration**:
   - A deterministic session mapping table guarantees that an identifier receives the exact same surrogate across arbitrary conversational turns (verified up to 40 turns), and silently reverses the surrogates in the assistant's output back to original student values.
4. **CLI & Audit Subsystem**:
   - Complete command-line interface supporting `redact`, `restore`, an interactive live `demo` harness for screen-share evaluation, batch directory processing, tabular CSV processing, and an interactive HTML transparency panel.
5. **Evaluation Benchmark**:
   - 50 hand-labeled synthetic education records evaluating detection precision and recall across 10 academic scenarios, backed by an automated evaluation pipeline (`src/promptshield/evaluate.py`).

---

## 2. What I Would Do Differently

Reflecting on the initial design and the empirical failure modes identified during evaluation:

1. **Hybrid Architecture (Regex Rules + Local SLM/NER) Over Pure Pattern Matching**:
   - While regex matching is fast and deterministic for structured tokens (Aadhaar, PAN, Roll No), it struggles with Indian proper names in free-form narrative Statement of Purpose essays lacking honorifics or headers.
   - A dual-layer approach would be superior: fast pattern filters for structured checksums, combined with a lightweight, quantized on-device token classifier (e.g., Indic-BERT via ONNX Runtime Web) for unstructured narrative entities.
2. **Context-Aware Numerical Disambiguation**:
   - Unprefixed 6-digit postal PIN codes present a collision risk with exam ranks or admission roll numbers. Contextual slot-filling dependency parsers are needed to avoid reliance on explicit keyword prefixes (`PIN Code:`, `Roll No:`).
3. **Token Normalization Prior to Regex Application**:
   - Line breaks and OCR hyphenation artifacts in digitized student marksheets and certificates split contiguous digit sequences. We implemented an upstream normalizer to heal these artifacts prior to regex scanning.

---

## 3. What Would Be Needed to Make It Work at Scale

Transitioning Prompt Shield from a CLI prototype to a production-grade browser extension deployed across thousands of universities and education portals requires four critical architectural pillars:

### A. Manifest V3 Browser Extension Architecture
- **In-DOM Interceptor**: Content script hooking into `<textarea>` and contenteditable DOM elements on ChatGPT (`chatgpt.com`), Claude (`claude.ai`), and Gemini (`gemini.google.com`).
- **Input Pipeline**: Intercept the dispatch event on the submit button, run local redaction synchronously in under 15 milliseconds, update the input buffer with surrogates, and allow transmission.
- **Output Observer**: A `MutationObserver` listening to incoming streaming response chunks from the LLM, silently substituting surrogates back to original student values before DOM rendering.

### B. Client-Side On-Device Inference (Zero Network Exfiltration)
- Deployment of models directly into the browser execution sandbox using **ONNX Runtime Web** (WebAssembly / WebGPU backend) and **Transformers.js**.
- Strict Content Security Policy (CSP) headers ensuring that zero network calls leave the extension for detection or mapping purposes. All mapping states remain strictly inside local browser memory.

### C. Persistent Session Vault via IndexedDB
- Replace file-based JSON session mappings with an encrypted client-side **IndexedDB** database keyed by conversation URL or session ID.
- Enable automatic TTL expiration and secure memory wipes when the user closes their browser tab or clears conversation history.

### D. Streaming Token De-Anonymization
- In production, LLMs stream tokens incrementally via Server-Sent Events (SSE). Reversing multi-token surrogates requires a streaming Aho-Corasick or prefix-tree trie buffer that matches and replaces surrogates across partial token boundaries without buffering entire model outputs.
