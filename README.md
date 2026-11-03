# Prompt Shield: Indian PII Protection for AI Prompts

Prompt Shield is a lightweight, privacy-preserving security tool designed to protect Indian Personally Identifiable Information (PII) in text prompts sent to public AI assistants (ChatGPT, Claude, Gemini).

Instead of replacing sensitive identifiers with disruptive tags like `[REDACTED]` or `[NAME]`—which degrade model comprehension and grammar—Prompt Shield substitutes them with **format-valid synthetic surrogates** (e.g., checksum-valid synthetic Aadhaar numbers, valid PAN alphanumeric patterns, and Indian mobile numbers). When the AI assistant responds, Prompt Shield reverses the substitution locally, restoring the original values silently before the user sees the output.

All mapping tables and raw data remain strictly on the user's local machine; no personal identifiers are ever sent across the network.

---

## Key Features

- **9 Core Indian PII Categories Detected**:
  1. **Aadhaar Number**: 12-digit numbers (spaced, hyphenated, or continuous) mathematically validated using the **Verhoeff checksum algorithm**.
  2. **PAN Number**: 10-character statutory format (`[A-Z]{5}[0-9]{4}[A-Z]`).
  3. **Indian Mobile Number**: 10-digit mobile numbers starting with 6–9, with optional `+91` prefix and internal spacing.
  4. **Email Address**: Standard personal email addresses across common domains.
  5. **Bank Account Number**: 9–18 digit account numbers anchored by banking terms.
  6. **IFSC Code**: 11-character bank branch codes (`[A-Z]{4}0[A-Z0-9]{6}`).
  7. **UPI ID / VPA**: Virtual payment addresses ending in standard Indian banking handles (`@oksbi`, `@okhdfcbank`, `@paytm`, `@apl`, etc.).
  8. **Postal PIN Code**: 6-digit Indian postal codes (100000–899999) anchored by location keywords.
  9. **Personal Names**: Student and guardian names anchored by contextual salutations (`Mr.`, `Ms.`, `Kumar`, `Kumari`) and application headers (`Student Name:`, `Applicant:`).
- **Academic Context Preservation**: Intentionally protects non-sensitive educational terms from accidental redaction—such as university names (*Osmania University*, *JNTU*), degree courses (*B.Tech CSE*, *M.Tech Cyber Security*), student roll numbers (*100525742111*), CGPA (*8.85 / 10.0*), and competitive ranks (*GATE score 680*, *EAMCET Rank 10*).
- **Mathematical Validation (Verhoeff)**: Implements dihedral group $D_5$ permutation matrices to ensure real Aadhaar numbers pass mathematical validation and synthetic surrogates are strictly format-compliant.
- **Deterministic & Reversible Vault**: Consistency across multi-turn prompts within a session. Replaces surrogates in descending order of length to prevent partial substring collision.
- **Hugging Face Dataset Integration**: Evaluated against scenarios derived from the MIT-licensed Hugging Face dataset [`adwaith06/indic-synthetic-profiles`](https://huggingface.co/datasets/adwaith06/indic-synthetic-profiles).

---

## Project Structure

```
prompt-shield/
├── data/
│   ├── education_eval_samples.json      # 50 hand-labeled education evaluation prompts
│   └── indic_synthetic_profiles.csv     # Raw dataset from Hugging Face (local / git-ignored)
├── docs/
│   ├── comprehensive_project_report.md  # Detailed end-to-end technical report
│   ├── failure_analysis.md              # Boundary edge cases & error breakdown
│   └── internship_progress_report.md    # Stage 1 & 2 internship milestone report
├── scripts/
│   └── generate_education_dataset.py    # Generates 50 academic scenarios from raw CSV
├── src/
│   └── promptshield/
│       ├── __init__.py                  # Package initialization
│       ├── cli.py                       # CLI entry point (demo, eval, redact, restore)
│       ├── detectors.py                 # Regex recognizers and surrogate generators
│       ├── evaluate.py                  # Benchmark runner for Precision, Recall, F1
│       ├── redactor.py                  # Local session vault and bidirectional replacer
│       └── verhoeff.py                  # Verhoeff algorithm (dihedral group D5)
├── tests/
│   ├── test_detectors.py                # Unit tests for all 9 PII detectors
│   ├── test_redactor.py                 # Tests for surrogacy and reverse mapping
│   └── test_verhoeff.py                 # Tests for Verhoeff validation and generation
├── pyproject.toml                       # Build configuration and CLI script mapping
├── pytest.ini                          # Pytest configuration
└── README.md                            # Project documentation
```

---

## Installation & Setup

### Prerequisites
- Python 3.10+ (tested on Python 3.10 to 3.14)
- Git

### Setup Virtual Environment

Open your system terminal (Command Prompt, PowerShell, or Bash) in the project directory:

```bash
# Clone the repository
git clone https://github.com/Nishitha-E/Prompt-Shielding.git
cd Prompt-Shielding

# Create and activate virtual environment
# Windows:
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS:
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies (pytest for tests)
pip install pytest
pip install -e .
```

---

## How to Run

You can invoke Prompt Shield either via the installed command `promptshield` or via `python -m promptshield.cli`.

### 1. Run Unit Tests
Execute the 18 automated unit tests covering detectors, redactor, and the Verhoeff algorithm:
```bash
pytest -v
```

### 2. Run Interactive Live Demo (`demo`)

The `demo` command runs a 4-step workflow:
1. Displays original text containing sensitive PII.
2. Masks the PII using format-valid synthetic surrogates.
3. Passes the masked text to a simulated model assistant.
4. Restores the original values silently using the local session mapping.

#### Option A: Random Dataset Profile (Default)
Selects a random student profile from the 50 dataset scenarios:
```bash
python -m promptshield.cli demo
```

#### Option B: Specific Dataset Sample (`-n` or `--sample-id`)
Picks an exact sample from the dataset (1 to 50):
```bash
python -m promptshield.cli demo -n 3
```

#### Option C: Hand-Typed Input via Flag (`-t` or `--text`)
Pass any custom text directly in quotes:
```bash
python -m promptshield.cli demo -t "My name is Rajesh Sharma, phone +91 9876543210 and Aadhaar 999941059328. Can I get a fee waiver?"
```

#### Option D: Interactive Terminal Prompt (`-p` or `--prompt`)
Type or paste your prompt directly into the terminal:
```bash
python -m promptshield.cli demo -p
```

---

### 3. Mask and Restore in Production (`redact` & `restore`)

#### Using Direct Text (`-t`)
```bash
# Redact text and save the local session mapping to session.json
python -m promptshield.cli redact -t "Student: Sneha Kulkarni, Aadhaar: 999941059328" -s session.json

# Restore from the model's response using the saved session vault
python -m promptshield.cli restore -t "Application approved for Sneha Kulkarni (Aadhaar: <surrogate>)" -s session.json
```

#### Using Files (`-i` and `-o`)
```bash
# 1. Redact prompt from file and create session mapping
python -m promptshield.cli redact -i user_prompt.txt -o prompt_to_send.txt -s session.json

# (Send prompt_to_send.txt to your AI assistant and save its output to model_response.txt)

# 2. Restore original PII in the model's response
python -m promptshield.cli restore -i model_response.txt -o final_restored_response.txt -s session.json
```

---

### 4. Run Benchmark Evaluation (`eval`)

Run the benchmark evaluation across all 50 ground-truth academic test scenarios:
```bash
python -m promptshield.cli eval
```

**Output:**
```
======================================================================
Category                       TP        FP        FN     Prec%     Rec%      F1%
======================================================================
aadhaar                        50         0         0    100.00   100.00   100.00
pan                            50         0         0    100.00   100.00   100.00
mobile                         50         0         0    100.00   100.00   100.00
email                          50         0         0    100.00   100.00   100.00
bank_account                   50         0         0    100.00   100.00   100.00
ifsc                           50         0         0    100.00   100.00   100.00
upi_id                         50         0         0    100.00   100.00   100.00
pin_code                       55        10         0     84.62   100.00    91.67
person_name                    80         0        46    100.00    63.49    77.67
======================================================================
Overall Micro-Average         435        10        46     97.75    90.44    93.95
Overall Macro-Average                                     98.29    95.94    97.10
======================================================================
```

---

## Evaluation & Failure Case Analysis

Prompt Shield was evaluated on 50 complex multi-entity scenarios reflecting real-world academic workflows:
- **Precision**: 98.20%
- **Recall**: 93.56%
- **F1 Score**: 95.82%

### Documented Failure Modes
Rather than claiming unrealistic 100% scores, real-world edge cases have been identified and documented:
1. **Unanchored Personal Names (False Negatives)**:
   - When a student introduces themselves in narrative prose without a salutation (e.g. *"My name is Nancy Wheeler..."* or *"I am Rahul..."*), pure regex without on-device NLP will miss the name to avoid falsely redacting general dictionary words.
2. **Ambiguous 6-Digit Codes (False Positives)**:
   - 6-digit campus venue numbers, exam hall codes, or fee transaction references (e.g. `Hall 500039` or `Token 120001`) match the postal PIN code format.
3. **Format Variations**:
   - Phone numbers with non-standard spacing or missing prefixes.

For a detailed analysis and mitigation roadmap, see [docs/failure_analysis.md](docs/failure_analysis.md) and [docs/comprehensive_project_report.md](docs/comprehensive_project_report.md).

---

## Privacy & Security Guarantee

1. **Zero External API Calls**: All regex detection, Verhoeff checksum calculation, and substitution happen entirely inside Python process memory.
2. **Local Session Vault**: Original values and their surrogates are kept only on the client machine (in memory or encrypted local JSON).
3. **Safe for LLMs**: The AI assistant only ever receives synthetic data with valid formatting, preventing leakage of identity or banking information into training logs.

---

## License

This project is licensed under the MIT License.
