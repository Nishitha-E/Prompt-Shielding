import csv
from pathlib import Path
from promptshield.redactor import PromptShieldEngine

class TabularSanitizer:
    def __init__(self, engine=None):
        self.engine=engine or PromptShieldEngine(seed=42)

    def sanitize_csv(self, input_file, output_file, text_columns=None, session_file=None):
        inp=Path(input_file)
        out=Path(output_file)
        out.parent.mkdir(parents=True, exist_ok=True)

        if session_file and Path(session_file).exists():
            self.engine.load_session(session_file)

        rows_processed=0
        with open(inp, mode="r", encoding="utf-8", newline="") as infile:
            reader=csv.DictReader(infile)
            fieldnames=reader.fieldnames or []

            target_cols=text_columns or [
                col for col in fieldnames
                if any(kw in col.lower() for kw in ["name", "id", "contact", "phone", "email", "query", "profile", "note", "address"])
            ]

            sanitized_rows=[]
            for row in reader:
                sanitized_row=dict(row)
                for col in target_cols:
                    if col in sanitized_row and sanitized_row[col]:
                        sanitized_row[col]=self.engine.redact(sanitized_row[col])
                sanitized_rows.append(sanitized_row)
                rows_processed += 1

        with open(out, mode="w", encoding="utf-8", newline="") as outfile:
            writer=csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(sanitized_rows)

        if session_file:
            self.engine.save_session(session_file)

        return {
            "rows_processed": rows_processed,
            "target_columns": target_cols,
            "total_pii_entities": len(self.engine.mapping),
            "output_file": str(out)
        }
