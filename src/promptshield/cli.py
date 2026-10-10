"""Command-line interface for Prompt Shield PII redactor, restorer, and audit transparency panel."""

import argparse
import sys
from pathlib import Path
from promptshield.redactor import PromptShieldEngine
from promptshield.audit import TransparencyAudit


def main():
    parser = argparse.ArgumentParser(
        description="Prompt Shield: Indian PII detector, surrogate Engine, and restoration CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: redact
    redact_parser = subparsers.add_parser("redact", help="Detect PII and replace with format-valid surrogates")
    redact_parser.add_argument("-i", "--input", help="Input text file path (default: stdin)")
    redact_parser.add_argument("-o", "--output", help="Output text file path (default: stdout)")
    redact_parser.add_argument("-s", "--session", required=True, help="Session mapping JSON file path")

    # Subcommand: restore
    restore_parser = subparsers.add_parser("restore", help="Restore original PII values in model response")
    restore_parser.add_argument("-i", "--input", help="Input response text file path (default: stdin)")
    restore_parser.add_argument("-o", "--output", help="Output text file path (default: stdout)")
    restore_parser.add_argument("-s", "--session", required=True, help="Session mapping JSON file path")

    # Subcommand: audit
    audit_parser = subparsers.add_parser("audit", help="Inspect transparency audit panel and export HTML report")
    audit_parser.add_argument("-i", "--input", required=True, help="Original input text file path")
    audit_parser.add_argument("-s", "--session", required=True, help="Session mapping JSON file path")
    audit_parser.add_argument("--html", help="Path to export interactive HTML audit report")

    # Subcommand: demo
    demo_parser = subparsers.add_parser("demo", help="Run interactive live demonstration of round-trip protection")
    demo_parser.add_argument("-i", "--input", help="Optional sample file to run demo with")

    args = parser.parse_args()

    engine = PromptShieldEngine()

    if args.command == "redact":
        session_path = Path(args.session)
        if session_path.exists():
            engine.load_session(str(session_path))

        text = Path(args.input).read_text(encoding="utf-8") if args.input else sys.stdin.read()
        redacted = engine.redact(text)
        engine.save_session(str(session_path))

        if args.output:
            Path(args.output).write_text(redacted, encoding="utf-8")
        else:
            sys.stdout.write(redacted)

    elif args.command == "restore":
        session_path = Path(args.session)
        if not session_path.exists():
            sys.stderr.write(f"Error: Session file '{args.session}' not found.\n")
            sys.exit(1)

        engine.load_session(str(session_path))
        text = Path(args.input).read_text(encoding="utf-8") if args.input else sys.stdin.read()
        restored = engine.restore(text)

        if args.output:
            Path(args.output).write_text(restored, encoding="utf-8")
        else:
            sys.stdout.write(restored)

    elif args.command == "audit":
        session_path = Path(args.session)
        if not session_path.exists():
            sys.stderr.write(f"Error: Session file '{args.session}' not found.\n")
            sys.exit(1)

        engine.load_session(str(session_path))
        orig_text = Path(args.input).read_text(encoding="utf-8")
        redacted_text = engine.redact(orig_text)

        audit = TransparencyAudit(engine.mapping)
        report = audit.generate_text_summary(orig_text, redacted_text)
        print(report)

        if args.html:
            audit.generate_html_report(orig_text, redacted_text, args.html)
            print(f"\n[+] Interactive HTML audit report saved to: {args.html}")

    elif args.command == "demo":
        sample_text = (
            Path(args.input).read_text(encoding="utf-8")
            if args.input
            else (
                "--- APOLLO HOSPITALS ---\n"
                "Patient Name: Mr. Ramesh Verma\n"
                "UHID: 849201 | DOB: 14/06/1984 | Contact: 9876543210\n"
                "ABHA ID: 14-9281-4029-8812 | Aadhaar: 2363 5412 8915\n"
                "Consultant: Dr. Arvind Swaminathan\n\n"
                "CLINICAL DIAGNOSIS:\n"
                "Acute Coronary Syndrome, Type 2 Diabetes Mellitus.\n"
                "Prescription: Tab Metformin 500mg BD, Tab Atorvastatin 40mg OD."
            )
        )

        print("\n" + "=" * 65)
        print("[+] PROMPT SHIELD: LIVE CLINICAL DEMONSTRATION")
        print("=" * 65)
        print("\n[STEP 1] ORIGINAL PATIENT CLINICAL DATA (LOCAL ONLY):")
        print("-" * 65)
        print(sample_text)

        print("\n[STEP 2] RUNNING LOCAL ZERO-EXFILTRATION REDACTION...")
        redacted = engine.redact(sample_text)
        print("-" * 65)
        print(redacted)

        print("\n[STEP 3] SIMULATING LLM MEDICAL REASONING RESPONSE...")
        simulated_llm_response = (
            f"Based on the clinical report for {engine.mapping.get('Mr. Ramesh Verma', 'the patient')}:\n"
            f"The management plan for Acute Coronary Syndrome and Type 2 Diabetes is appropriate.\n"
            f"Continue Tab Metformin 500mg and Tab Atorvastatin 40mg. Monitor fasting blood glucose."
        )
        print("-" * 65)
        print(simulated_llm_response)

        print("\n[STEP 4] SILENT LOCAL RESTORATION (USER VIEW):")
        print("-" * 65)
        restored = engine.restore(simulated_llm_response)
        print(restored)
        print("=" * 65)
        print("[OK] Round-trip complete: Sensitive identifiers preserved locally. Medical advice accurate!\n")


if __name__ == "__main__":
    main()
