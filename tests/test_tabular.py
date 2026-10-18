"""Unit tests for TabularSanitizer CSV medical dataset processing."""

import csv
from pathlib import Path
from promptshield.tabular import TabularSanitizer
from promptshield.verhoeff import generate_verhoeff_number


def test_sanitize_clinical_csv(tmp_path):
    input_csv = tmp_path / "raw_clinical.csv"
    output_csv = tmp_path / "sanitized_clinical.csv"
    session_file = tmp_path / "tabular_session.json"

    valid_aadhaar = generate_verhoeff_number("23635412891")
    rows = [
        {
            "row_id": "1",
            "patient_name": "Mr. Ramesh Verma",
            "aadhaar": f"{valid_aadhaar[:4]} {valid_aadhaar[4:8]} {valid_aadhaar[8:]}",
            "clinical_notes": "Patient: Mr. Ramesh Verma admitted with Acute Pancreatitis. Contact: 9876543210.",
            "diagnosis": "Acute Pancreatitis, resolving",
            "rx": "Tab Pantoprazole 40mg OD"
        },
        {
            "row_id": "2",
            "patient_name": "Mrs. Sunita Sharma",
            "aadhaar": "981240192841",
            "clinical_notes": "Consultant: Dr. Arvind Swaminathan. Prescribed Metformin 500mg.",
            "diagnosis": "Type 2 Diabetes",
            "rx": "Tab Metformin 500mg BD"
        }
    ]

    with open(input_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    sanitizer = TabularSanitizer()
    summary = sanitizer.sanitize_csv(
        input_file=str(input_csv),
        output_file=str(output_csv),
        session_file=str(session_file)
    )

    assert summary["rows_processed"] == 2
    assert output_csv.exists()

    with open(output_csv, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
        assert len(reader) == 2
        
        # Patient identifiers redacted
        assert "Ramesh Verma" not in reader[0]["patient_name"]
        assert "Ramesh Verma" not in reader[0]["clinical_notes"]
        assert "9876543210" not in reader[0]["clinical_notes"]

        # Clinical medical info preserved
        assert "Acute Pancreatitis" in reader[0]["diagnosis"]
        assert "Tab Pantoprazole 40mg OD" in reader[0]["rx"]
        assert "Type 2 Diabetes" in reader[1]["diagnosis"]
        assert "Tab Metformin 500mg BD" in reader[1]["rx"]
