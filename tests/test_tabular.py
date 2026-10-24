import csv
from pathlib import Path
from promptshield.tabular import TabularSanitizer
from promptshield.verhoeff import generate_verhoeff_number

def test_sanitize_student_profile_csv(tmp_path):
    input_csv=tmp_path / "raw_students.csv"
    output_csv=tmp_path / "sanitized_students.csv"
    session_file=tmp_path / "tabular_session.json"

    valid_aadhaar=generate_verhoeff_number("23635412891")
    rows=[
        {
            "student_id": "OU-101",
            "student_name": "Mr. Rajesh Sharma",
            "aadhaar": f"{valid_aadhaar[:4]} {valid_aadhaar[4:8]} {valid_aadhaar[8:]}",
            "student_query": "Student Name: Mr. Rajesh Sharma applying for M.E. Cyber Security. Contact: 9876543210.",
            "course": "M.E. Cyber Security",
            "scholarship": "ePASS Eligible"
        },
        {
            "student_id": "OU-102",
            "student_name": "Ms. Sunita Patel",
            "aadhaar": "981240192841",
            "student_query": "Student Name: Ms. Sunita Patel requesting hostel room allotment.",
            "course": "B.Tech CSE",
            "scholarship": "Merit Scholarship"
        }
    ]

    with open(input_csv, "w", encoding="utf-8", newline="") as f:
        writer=csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    sanitizer=TabularSanitizer()
    summary=sanitizer.sanitize_csv(
        input_file=str(input_csv),
        output_file=str(output_csv),
        session_file=str(session_file)
    )

    assert summary["rows_processed"] == 2
    assert output_csv.exists()

    with open(output_csv, "r", encoding="utf-8") as f:
        reader=list(csv.DictReader(f))
        assert len(reader) == 2

        # PII replaced
        assert "Rajesh Sharma" not in reader[0]["student_name"]
        assert "Rajesh Sharma" not in reader[0]["student_query"]
        assert "9876543210" not in reader[0]["student_query"]

        # Academic context preserved
        assert reader[0]["course"] == "M.E. Cyber Security"
        assert reader[0]["scholarship"] == "ePASS Eligible"
        assert reader[1]["course"] == "B.Tech CSE"
