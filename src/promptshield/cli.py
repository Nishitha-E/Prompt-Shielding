import argparse
import sys
from pathlib import Path
from promptshield.redactor import PromptShieldEngine
from promptshield.evaluate import evaluate_dataset, print_evaluation_report

def main():
    parser = argparse.ArgumentParser(description="Prompt Shield PII Redactor")
    subparsers = parser.add_subparsers(dest="command", required=True)

    redact_p = subparsers.add_parser("redact", help="Redact PII in text")
    redact_p.add_argument("-i", "--input", help="Input file path")
    redact_p.add_argument("-o", "--output", help="Output file path")
    redact_p.add_argument("-s", "--session", required=True, help="Session json file")

    restore_p = subparsers.add_parser("restore", help="Restore PII from model response")
    restore_p.add_argument("-i", "--input", help="Input file path")
    restore_p.add_argument("-o", "--output", help="Output file path")
    restore_p.add_argument("-s", "--session", required=True, help="Session json file")

    demo_p = subparsers.add_parser("demo", help="Run live demo")
    demo_p.add_argument("-i", "--input", help="Optional sample file")

    eval_p = subparsers.add_parser("eval", help="Run evaluation benchmark")
    eval_p.add_argument("-d", "--dataset", default="data/education_eval_samples.json", help="Path to samples json")

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
            sys.stderr.write(f"Session file not found: {args.session}\n")
            sys.exit(1)

        engine.load_session(str(session_path))
        text = Path(args.input).read_text(encoding="utf-8") if args.input else sys.stdin.read()
        restored = engine.restore(text)

        if args.output:
            Path(args.output).write_text(restored, encoding="utf-8")
        else:
            sys.stdout.write(restored)

    elif args.command == "demo":
        sample = (
            Path(args.input).read_text(encoding="utf-8") if args.input else (
                "Osmania University Student Enquiry\n"
                "Student Name: Mr. Rajesh Sharma\n"
                "Roll No: 1005-26-701, Application No: OU26-49102\n"
                "Course: M.E. Cyber Security\n"
                "DOB: 14/06/2002, Aadhaar: 2363 5412 8915, PAN: ABCPK1234Z\n"
                "Contact: 9876543210, Email: rajesh.sharma@gmail.com\n"
                "Bank A/c No: 38491029481, IFSC: SBIN0001234, Fee UPI: rajesh@oksbi\n"
                "Address PIN Code: 500007\n\n"
                "Query: Applying for fee reimbursement. GATE Score: 680, CGPA: 8.85."
            )
        )
        print("Prompt Shield Demo")
        print("\n[Step 1] Original Text:")
        print(sample)
        redacted = engine.redact(sample)
        print("\n[Step 2] Redacted Text:")
        print(redacted)
        student_surrogate = engine.mapping.get("Rajesh Sharma", engine.mapping.get("Mr. Rajesh Sharma", "the student"))
        llm_response = (
            f"Regarding {student_surrogate}: Eligibility for fee reimbursement is verified based on GATE 680 and CGPA 8.85."
        )
        print("\n[Step 3] Simulated Model Response:")
        print(llm_response)
        restored = engine.restore(llm_response)
        print("\n[Step 4] Restored Response:")
        print(restored)

    elif args.command == "eval":
        results = evaluate_dataset(args.dataset)
        print_evaluation_report(results)

if __name__ == "__main__":
    main()
