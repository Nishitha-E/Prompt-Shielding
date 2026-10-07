"""Command-line interface for Prompt Shield PII redactor and restorer."""

import argparse
import sys
from pathlib import Path
from promptshield.redactor import PromptShieldEngine


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

    args = parser.parse_args()

    engine = PromptShieldEngine()
    session_path = Path(args.session)

    if args.command == "redact":
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


if __name__ == "__main__":
    main()
