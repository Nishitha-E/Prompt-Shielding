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

    # Subcommand: benchmark
    benchmark_parser = subparsers.add_parser("benchmark", help="Measure redaction latency and throughput")
    benchmark_parser.add_argument("-d", "--dataset", default="data/medical_eval_samples.json", help="Dataset path")
    benchmark_parser.add_argument("-n", "--iterations", type=int, default=5, help="Number of test iterations")

    # Subcommand: batch
    batch_parser = subparsers.add_parser("batch", help="Batch sanitize a directory of clinical text documents")
    batch_parser.add_argument("-i", "--input-dir", required=True, help="Input directory containing documents")
    batch_parser.add_argument("-o", "--output-dir", required=True, help="Output directory for sanitized documents")
    batch_parser.add_argument("-s", "--session", help="Optional session mapping JSON file path")

    # Subcommand: tabular
    tabular_parser = subparsers.add_parser("tabular", help="Sanitize a clinical CSV dataset or table")
    tabular_parser.add_argument("-i", "--input", required=True, help="Input CSV file path")
    tabular_parser.add_argument("-o", "--output", required=True, help="Output sanitized CSV file path")
    tabular_parser.add_argument("-s", "--session", help="Optional session mapping JSON file path")

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
                "--- UNIVERSITY COLLEGE OF ENGINEERING, OSMANIA UNIVERSITY ---\n"
                "STUDENT SCHOLARSHIP & ADMISSION ENQUIRY\n"
                "Student Name: Mr. Rajesh Sharma\n"
                "Roll No: 1005-26-701 | Application No: OU26-49102\n"
                "Course: M.E. Cyber Security (Semester 1)\n"
                "DOB: 14/06/2002 | Aadhaar: 2363 5412 8915 | PAN: ABCPK1234Z\n"
                "Contact: 9876543210 | Email: rajesh.sharma@gmail.com\n"
                "Bank A/c No: 38491029481 | IFSC: SBIN0001234 | Fee UPI: rajesh@oksbi\n"
                "Address PIN Code: 500007\n\n"
                "QUERY:\n"
                "Applying for Post-Matric Scholarship fee waiver of Rs. 35,000 for M.E. Cyber Security.\n"
                "GATE 2026 Score: 680, B.Tech CGPA: 8.85 / 10.0. Please confirm eligibility."
            )
        )

        print("\n" + "=" * 65)
        print("[+] PROMPT SHIELD: LIVE EDUCATION SECTOR DEMONSTRATION")
        print("=" * 65)
        print("\n[STEP 1] ORIGINAL STUDENT SENSITIVE DATA (LOCAL ONLY):")
        print("-" * 65)
        print(sample_text)

        print("\n[STEP 2] RUNNING LOCAL ZERO-EXFILTRATION REDACTION...")
        redacted = engine.redact(sample_text)
        print("-" * 65)
        print(redacted)

        print("\n[STEP 3] SIMULATING LLM ASSISTANT RESPONSE...")
        student_surrogate = engine.mapping.get('Rajesh Sharma', engine.mapping.get('Mr. Rajesh Sharma', 'the student'))
        simulated_llm_response = (
            f"Based on the application for {student_surrogate}:\n"
            f"Your eligibility for the Post-Matric Scholarship in M.E. Cyber Security at Osmania University is verified.\n"
            f"With a GATE score of 680 and CGPA 8.85, you satisfy the merit criteria. Proceed with online document submission."
        )
        print("-" * 65)
        print(simulated_llm_response)

        print("\n[STEP 4] SILENT LOCAL RESTORATION (USER VIEW):")
        print("-" * 65)
        restored = engine.restore(simulated_llm_response)
        print(restored)
        print("=" * 65)
        print("[OK] Round-trip complete: Sensitive identifiers protected. Academic context preserved!\n")

    elif args.command == "benchmark":
        from promptshield.benchmarks import run_latency_benchmark, print_benchmark_report
        b = run_latency_benchmark(dataset_path=args.dataset, iterations=args.iterations)
        print_benchmark_report(b)

    elif args.command == "batch":
        from promptshield.batch import BatchProcessor
        processor = BatchProcessor(engine=engine)
        summary = processor.process_directory(
            input_dir=args.input_dir,
            output_dir=args.output_dir,
            session_file=args.session
        )
        print("=" * 65)
        print(" PROMPT SHIELD: BATCH SANITIZATION SUMMARY")
        print("=" * 65)
        print(f"Total Files Processed    : {summary['total_files']}")
        print(f"Total Unique PII Mapped  : {summary['total_pii_entities']}")
        print(f"Total Processing Time    : {summary['total_elapsed_ms']} ms")
        print(f"Sanitized Directory      : {args.output_dir}")
        print("=" * 65)

    elif args.command == "tabular":
        from promptshield.tabular import TabularSanitizer
        sanitizer = TabularSanitizer(engine=engine)
        summary = sanitizer.sanitize_csv(
            input_file=args.input,
            output_file=args.output,
            session_file=args.session
        )
        print("=" * 65)
        print(" PROMPT SHIELD: TABULAR CSV SANITIZATION SUMMARY")
        print("=" * 65)
        print(f"Rows Processed           : {summary['rows_processed']}")
        print(f"Sanitized Columns        : {', '.join(summary['target_columns'])}")
        print(f"Total Unique PII Mapped  : {summary['total_pii_entities']}")
        print(f"Output File              : {summary['output_file']}")
        print("=" * 65)


if __name__ == "__main__":
    main()
