import argparse
import json
import sys
from pathlib import Path
from promptshield.redactor import PromptShieldEngine
from promptshield.evaluate import evaluate_dataset, print_evaluation_report

def main():
    parser = argparse.ArgumentParser(description="Prompt Shield PII Redactor")
    subparsers = parser.add_subparsers(dest="command", required=True)

    redact_p = subparsers.add_parser("redact", help="Redact PII in text")
    redact_p.add_argument("-i", "--input", help="Input file path")
    redact_p.add_argument("-t", "--text", help="Direct hand-typed input text")
    redact_p.add_argument("-o", "--output", help="Output file path")
    redact_p.add_argument("-s", "--session", required=True, help="Session json file")

    restore_p = subparsers.add_parser("restore", help="Restore PII from model response")
    restore_p.add_argument("-i", "--input", help="Input file path")
    restore_p.add_argument("-t", "--text", help="Direct hand-typed response text")
    restore_p.add_argument("-o", "--output", help="Output file path")
    restore_p.add_argument("-s", "--session", required=True, help="Session json file")

    demo_p = subparsers.add_parser("demo", help="Run live demo")
    demo_p.add_argument("-i", "--input", help="Optional sample file")
    demo_p.add_argument("-t", "--text", help="Direct hand-typed text prompt to demo")
    demo_p.add_argument("-p", "--prompt", action="store_true", help="Interactive live typing mode")
    demo_p.add_argument("-n", "--sample-id", type=int, help="Sample number (1 to 50) from dataset")

    eval_p = subparsers.add_parser("eval", help="Run evaluation benchmark")
    eval_p.add_argument("-d", "--dataset", default="data/education_eval_samples.json", help="Path to samples json")

    args = parser.parse_args()
    engine = PromptShieldEngine()

    if args.command == "redact":
        session_path = Path(args.session)
        if session_path.exists():
            engine.load_session(str(session_path))

        if args.text:
            text = args.text
        elif args.input:
            text = Path(args.input).read_text(encoding="utf-8")
        else:
            text = sys.stdin.read()

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
        if args.text:
            text = args.text
        elif args.input:
            text = Path(args.input).read_text(encoding="utf-8")
        else:
            text = sys.stdin.read()

        restored = engine.restore(text)

        if args.output:
            Path(args.output).write_text(restored, encoding="utf-8")
        else:
            sys.stdout.write(restored)

    elif args.command == "demo":
        import random
        engine = PromptShieldEngine(seed=None)

        if args.text:
            sample = args.text
        elif args.prompt:
            print("Type or paste your prompt below (press Enter to finish):")
            sample = input("> ").strip()
        elif args.input:
            sample = Path(args.input).read_text(encoding="utf-8")
        else:
            dataset_path = Path("data/education_eval_samples.json")
            if dataset_path.exists():
                with open(dataset_path, "r", encoding="utf-8") as f:
                    dataset_samples = json.load(f)
                idx = (args.sample_id - 1) if (args.sample_id and 1 <= args.sample_id <= len(dataset_samples)) else random.randint(0, len(dataset_samples) - 1)
                chosen = dataset_samples[idx]
                sample = chosen["text"]
                print(f"Loading Dataset Sample #{chosen.get('id', idx+1)} ({chosen.get('college', 'University')})\n")
            else:
                sample = "Student Name: Sathish Shivaprasad\nAadhaar: 7430 3911 7183"

        print("Prompt Shield Demo")
        print("\n[Step 1] Original Text:")
        print(sample)
        redacted = engine.redact(sample)
        print("\n[Step 2] Redacted Text:")
        print(redacted)

        surrogate_name = "the student"
        for orig, surr in engine.mapping.items():
            if not any(ch.isdigit() for ch in orig) and "@" not in orig and len(orig.split()) >= 2:
                surrogate_name = surr
                break

        llm_response = f"Regarding {surrogate_name}: Your application details have been verified and academic eligibility is satisfied."
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
