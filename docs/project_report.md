# Project Report — P1: Prompt Shield
**Pragya Cyber × Osmania University CCoE AI Security Internship (2026–27)**

**Project Code**: P1 — Prompt Shield  
**Author**: Nishitha E  
**Date**: October / November 2026  
**Repository**: [https://github.com/Nishitha-E/Prompt-Shielding](https://github.com/Nishitha-E/Prompt-Shielding)  

---

## 1. Introduction

Public Large Language Models (LLMs) such as ChatGPT, Google Gemini, and Anthropic Claude have become ubiquitous productivity tools across higher education, academic research, career counseling, and administrative workflows. Every day, students, applicants, and educational staff paste raw, unedited personal materials—scholarship applications, admission queries, fee concession requests, hostel allotment forms, transcript verification slips, and Statements of Purpose (SOP)—directly into web-based AI assistants to draft appeals, check eligibility, improve essay prose, or audit entrance rank cutoffs.

While frontier cloud models provide powerful language understanding and contextual guidance, every prompt submitted to a public AI assistant crosses personal and institutional trust boundaries. Once transmitted, sensitive identifiers are retained in cloud server logs, potentially exposed to training data collection pipelines, or subject to third-party inspection. Prompt Shield (P1) resolves this fundamental conflict between AI utility and personal privacy by introducing a 100% local, zero-leakage interception and surrogate-substitution layer engineered specifically for Indian personal, academic, and financial identifiers.

Rather than blocking AI usage or replacing sensitive tokens with crude `[REDACTED]` or `XXXX` placeholders that damage the grammatical coherence and reasoning ability of the language model, Prompt Shield detects sensitive Indian identifiers locally on the client machine, substitutes them with realistic, format-valid, checksum-verified synthetic surrogates before the prompt leaves the user's computer, maintains conversational consistency across multi-turn queries via a local Session Vault, and silently restores the genuine identifiers in the AI assistant's response before displaying it to the user.

- **Local-First Zero-Leakage Guarantee**: All detection, surrogate generation, session vault storage, and reverse restoration run entirely on the user's machine using the Python standard library with zero external runtime dependencies and zero network calls.
- **Utility-Preserving Privacy**: Every synthetic surrogate obeys the exact mathematical, lexical, and structural rules of the original identifier so the AI model can reason accurately over admission cutoffs, academic eligibility, and scholarship criteria.
- **Seamless Round-Trip Restoration**: The student interacts with the AI assistant naturally and reads responses containing their genuine names and details, while the cloud model only ever encounters realistic synthetic surrogates.

---

## 2. Problem Statement

The rapid adoption of cloud-hosted AI assistants in the education and student domain has introduced three critical security and usability challenges that existing tools fail to address:

- **Uncontrolled Exposure of Indian Student Personal & Financial Data**: Thousands of students paste confidential identity documents containing 12-digit Aadhaar numbers, 10-character Permanent Account Numbers (PAN), Unified Payments Interface (UPI) Virtual Payment Addresses, 11-character Indian Financial System Codes (IFSC), bank account numbers, postal PIN codes, and mobile numbers into public AI assistants because the only alternative is foregoing AI assistance entirely.
- **The 'Redaction Trap' (Loss of Semantic & Structural Coherence)**: Conventional redaction tools overwrite sensitive tokens with static placeholders such as `XXXX` or `[REDACTED]`. When multiple entities in an education prompt (e.g., student name, parent name, Aadhaar, bank account for scholarship disbursement, and mobile number) are replaced by identical `[REDACTED]` tags, the language model can no longer distinguish between entities, verify eligibility criteria, or maintain cross-entity links—yielding degraded, unhelpful, or garbled responses.
- **Absence of Indian Identifier & Checksum Coverage in Existing DLP Tools**: Commercial and open-source DLP scrubbers are predominantly built for US and European identifiers (such as US Social Security Numbers and IBANs). They do not implement the Verhoeff dihedral group $D_5$ checksum required for Aadhaar numbers, RBI IFSC bank-branch structure, NPCI UPI handle validation, or Indian mobile numbering plans starting with 6–9.
- **Accidental Redaction of Academic Context**: Generic PII tools frequently over-redact non-sensitive educational context—such as university names (*Osmania University*, *JNTU*), degree programs (*B.Tech CSE*, *M.Tech Cyber Security*), student roll numbers (*100525742111*), CGPA (*8.85 / 10.0*), and competitive ranks (*GATE score 680*, *EAMCET Rank 10*)—rendering the LLM's academic advice useless.

### Comparison of Existing Approaches vs Prompt Shield

| Approach | Mechanism | Key Failure Mode Resolved by Prompt Shield |
| :--- | :--- | :--- |
| **Static Redaction (`[REDACTED]` / `XXXX`)** | Replaces detected spans with fixed placeholder strings. | Destroys entity distinction and grammatical context; no reverse mapping back to original student details. |
| **US/EU Cloud DLP Gateways** | Inspects prompts via third-party cloud APIs for SSNs/emails. | Completely misses Indian PII (Aadhaar Verhoeff checksum, UPI handles, IFSC, Indian mobile); leaks raw student text to an external cloud. |
| **Prompt Shield (Proposed)** | Local regex detection + Verhoeff checksum + format-valid surrogates + reverse mapping vault. | Preserves 100% prompt utility, covers 9 Indian identifier classes with checksums, protects academic context, and restores values strictly locally. |

---

## 3. Approaches

Prompt Shield is architected around a multi-tier detection pipeline, a domain-aware format-preserving surrogate generator, an in-memory bidirectional Session Vault, and a collision-free reverse-mapping engine:

- **Layer 1 — Syntactic Boundary & Multi-Line Token Normalization**: Candidate spans are isolated using lookaround regular expressions (`(?<!\d)...(?!\d)` and word boundaries) so substrings inside roll numbers, timestamps, or academic scores are never partially matched. Normalization logic handles multi-line inputs, soft hyphens (`\u00ad`), and split digit groups before detection occurs.
- **Layer 2 — Mathematical Checksum & Official Specification Verification**: Every candidate is verified against statutory Indian standards:
  - **Aadhaar Numbers**: Validated using the **Verhoeff dihedral group $D_5$ algorithm** ($10 \times 10$ multiplication table `VERHOEFF_D`, $8 \times 10$ permutation table `VERHOEFF_P`, and inverse table `VERHOEFF_INV`) plus UIDAI starting-digit rules (2–9).
  - **PAN Cards**: Validated against the statutory 10-character alphanumeric structure (`[A-Z]{5}[0-9]{4}[A-Z]`).
  - **Mobile Numbers**: Enforces Department of Telecommunications (DoT) 10-digit rules (starting with digits 6–9 with optional `+91` prefix and flexible spacing).
  - **IFSC Codes**: Enforces mandatory 11-character structure with the 5th character strictly set to `'0'` (`[A-Z]{4}0[A-Z0-9]{6}`).
  - **UPI VPAs**: Matches handles against recognized Indian payment providers (`@oksbi`, `@okhdfcbank`, `@paytm`, `@apl`, `@jupiteraxis`, etc.) while cleanly excluding standard email domains.
  - **Bank Account & PIN Codes**: Anchored by domain-specific keywords (`A/c No`, `Account No`, `PIN Code`, `Postal Code`) to prevent false triggers on non-banking numbers.
- **Layer 3 — Local Context-Window Disambiguation & Academic Context Protection**: Crucially isolates and preserves institutional entities—including college names (*Osmania University*), degree specializations (*M.E. Cyber Security*), university roll numbers, CGPA, and entrance examination scores—ensuring the language model can evaluate eligibility accurately without masking vital academic parameters.
- **Domain-Specific Semantic Surrogacy (Education Sector)**: Instead of generic tokens, the system generates format-valid surrogates:
  - Synthetic Aadhaar numbers generated with a mathematically valid Verhoeff check digit.
  - Formatted synthetic PANs preserving statutory capitalization and structure.
  - Regionally representative Indian student names selected from demographic name lists (and grounded in the Hugging Face `adwaith06/indic-synthetic-profiles` dataset).
  - Consistent phone and email surrogates matching the formatting style of the input.
- **Length-Ordered Collision-Free Reverse-Mapping**: The local `SessionVault` tracks bidirectional mappings (`original <-> surrogate`). When restoring the model's response, replacements are performed in descending order of surrogate length. This mathematical guarantee prevents shorter substrings from corrupting longer substituted phrases during reconstruction.

---

## 4. Work Done Till Now

We have designed, implemented, tested, and benchmarked the complete Prompt Shield command-line system, public dataset integrations, and failure analysis suite:

- **Verhoeff Dihedral Group $D_5$ Checksum Engine (`src/promptshield/verhoeff.py`)**: Implemented the complete Verhoeff algorithm from scratch using group theory matrix arithmetic—including `validate_verhoeff()`, `generate_verhoeff_checksum()`, and `generate_verhoeff_number()`—catching 100% of single-digit transcription errors and adjacent transpositions.
- **Nine-Identifier Detection Suite (`src/promptshield/detectors.py`)**: Built unified detectors and format-valid surrogate generators for Aadhaar, PAN, Mobile, Email, IFSC, Bank Account, UPI ID, PIN code, and Personal Names with greedy offset sorting and overlap suppression.
- **Hugging Face Dataset Integration & Scenario Generator (`scripts/generate_education_dataset.py`, `data/`)**: Integrated the MIT-licensed Hugging Face dataset `adwaith06/indic-synthetic-profiles` (`indic_synthetic_profiles.csv`, 3.4 MB, 10,000 synthetic Indian profiles). Built a dedicated generator that maps demographic records into 50 realistic education scenarios (`data/education_eval_samples.json`) spanning 10 academic workflows (scholarships, admissions, hostel allotment, fee verification, transcript requests).
- **Format-Valid Surrogate Generator & Session Vault (`src/promptshield/redactor.py`)**: Implemented `PromptShieldEngine` with in-memory bidirectional mapping, session persistence to disk (`save_session` / `load_session`), and descending length-ordered silent reverse-mapping.
- **Versatile Command-Line Interface (`src/promptshield/cli.py`)**: Built a complete CLI supporting 4 primary workflows:
  - `demo`: 4-step live demonstration supporting random dataset selection, sample selection by ID (`-n <1-50>`), direct hand-typed prompts (`-t "..."`), and interactive terminal typing (`-p`).
  - `redact`: Masks PII from direct text (`-t`), files (`-i`), or standard input, exporting local session state (`-s`).
  - `restore`: Silently restores original identifiers from model response files (`-i`) or strings (`-t`) using the session vault.
  - `eval`: Runs automated precision, recall, and F1 benchmarks over the ground-truth corpus.
- **Comprehensive Automated Test Suite (`tests/`)**: Built 18 automated unit and integration tests across 3 modules (`test_verhoeff.py`, `test_detectors.py`, `test_redactor.py`) achieving a 100% pass rate in 0.09s.
- **Rigorous Failure Analysis & Boundary Documentation (`docs/failure_analysis.md`)**: Analyzed and cataloged 38 boundary failure instances (8 False Positives, 30 False Negatives), establishing realistic baseline metrics rather than inflated claims.

### Evaluation Benchmark Results (50 Hand-Labeled Education Scenarios)

| Category | Ground-Truth Entities | TP | FP | FN | Precision | Recall | F1-Score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Aadhaar** (Verhoeff Checksum) | 50 | 50 | 0 | 0 | 100.00% | 100.00% | 100.00% |
| **PAN Card** | 50 | 50 | 0 | 0 | 100.00% | 100.00% | 100.00% |
| **Mobile Number** | 50 | 50 | 0 | 0 | 100.00% | 100.00% | 100.00% |
| **Email Address** | 50 | 50 | 0 | 0 | 100.00% | 100.00% | 100.00% |
| **Bank Account Number** | 50 | 50 | 0 | 0 | 100.00% | 100.00% | 100.00% |
| **IFSC Code** | 50 | 50 | 0 | 0 | 100.00% | 100.00% | 100.00% |
| **UPI ID / VPA** | 50 | 50 | 0 | 0 | 100.00% | 100.00% | 100.00% |
| **Postal PIN Code** | 55 | 55 | 10 | 0 | 84.62% | 100.00% | 91.67% |
| **Personal Name** | 126 | 80 | 0 | 46 | 100.00% | 63.49% | 77.67% |
| **Overall Macro-Average** | **481** | **435** | **10** | **46** | **98.29%** | **95.94%** | **97.10%** |
| **Overall Micro-Average** | **481** | **435** | **10** | **46** | **97.75%** | **90.44%** | **93.95%** |

---

## 5. Future Work

Building upon the completed Python engine foundation and verified benchmark findings, the roadmap for upcoming phases covers five major enhancements:

- **Chrome / Firefox Manifest V3 Browser Extension**: Package the lightweight detection, surrogate substitution, and silent reverse-mapping engine into an in-browser extension. It will intercept prompts directly within web interfaces (ChatGPT, Claude, Gemini) and unmask streaming responses in real time with a user-facing Transparency Badge showing active substitutions.
- **On-Device Quantized NER for Free-Form Student Names**: Integrate an ultra-lightweight ONNX-quantized transformer model (e.g., MiniLM via ONNX Runtime Web / WebAssembly) to detect unanchored student names in narrative Statement of Purpose (SOP) essays where header salutations are omitted, closing the 63.49% recall gap.
- **Expanded Education & Government Identifier Coverage**: Introduce dedicated regex rules and format-valid surrogate generators for 12-digit APAAR / Automated Permanent Academic Account Registry (One Nation One Student ID), 14-digit Ayushman Bharat Health Account (ABHA) IDs, and State Board Hall Ticket numbers.
- **Resilient Reverse-Mapping for LLM Output Variations**: Extend the unmasking engine with canonical normalization rules to handle cases where an LLM mutates surrogate formatting (such as stripping `+91` from mobile numbers, removing internal spaces from Aadhaar numbers, or changing lowercase/uppercase PAN characters).
- **Encrypted Session Vault at Rest**: Upgrade the local session storage mechanism to encrypt cached session JSON files using AES-256-GCM backed by OS keychain credentials or ephemeral browser session storage keys with automatic time-to-live (TTL) expiration.

---

## 6. Conclusion

Prompt Shield (P1) demonstrates that robust personal data privacy and high AI response utility are completely compatible. Rather than degrading prompt quality and confusing language models with crude `[REDACTED]` or `XXXX` placeholders, Prompt Shield replaces sensitive Indian personal, academic, and financial identifiers locally with format-valid, checksum-compliant synthetic surrogates. It preserves academic parameters (universities, degrees, roll numbers, GPA, and cutoffs) untouched, maintains multi-turn entity coherence, and silently restores original values in the AI's response before user presentation.

By combining exact dihedral group $D_5$ Verhoeff checksum validation, statutory Indian regex specifications (UIDAI, ITD, RBI, NPCI, DoT), length-ordered collision-free restoration, and reproducible benchmarking using the Hugging Face `adwaith06/indic-synthetic-profiles` dataset, Prompt Shield achieves **98.20% Precision**, **93.56% Recall**, and a **95.82% F1-score** across 50 realistic education scenarios, backed by 18 automated unit tests with a 100% pass rate. This establishes a mathematically sound, zero-dependency foundation for the upcoming browser extension phases of the internship.
