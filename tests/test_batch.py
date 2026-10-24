"""Unit tests for batch document processing subsystem."""

import json
from pathlib import Path
from promptshield.batch import BatchProcessor
from promptshield.redactor import PromptShieldEngine


def test_batch_directory_processing(tmp_path):
    input_dir = tmp_path / "raw_reports"
    output_dir = tmp_path / "sanitized_reports"
    session_file = tmp_path / "batch_session.json"
    input_dir.mkdir()

    # Create 3 sample student enquiries
    (input_dir / "report1.txt").write_text(
        "Student Name: Mr. Ramesh Verma\nRoll No: 1005-26-701\nCourse: M.E. Cyber Security.",
        encoding="utf-8"
    )
    (input_dir / "report2.txt").write_text(
        "Student Name: Mrs. Sunita Sharma\nRoll No: 1005-26-702\nCourse: B.Tech CSE.",
        encoding="utf-8"
    )
    (input_dir / "report3.txt").write_text(
        "Follow-up for Mr. Ramesh Verma with Roll No: 1005-26-701.",
        encoding="utf-8"
    )

    processor = BatchProcessor()
    summary = processor.process_directory(
        input_dir=str(input_dir),
        output_dir=str(output_dir),
        session_file=str(session_file)
    )

    assert summary["total_files"] == 3
    assert summary["total_pii_entities"] > 0
    assert (output_dir / "report1.txt").exists()
    assert (output_dir / "report2.txt").exists()
    assert (output_dir / "report3.txt").exists()
    assert (output_dir / "batch_manifest.json").exists()

    # Check that Ramesh Verma's surrogate is identical in report1 and report3
    rep1_text = (output_dir / "report1.txt").read_text(encoding="utf-8")
    rep3_text = (output_dir / "report3.txt").read_text(encoding="utf-8")

    assert "Ramesh Verma" not in rep1_text
    assert "Ramesh Verma" not in rep3_text

    # Verify session consistency: both files use the same surrogate
    surrogate_name = processor.engine.mapping["Mr. Ramesh Verma"]
    assert surrogate_name in rep1_text
    assert surrogate_name in rep3_text

    # Manifest verification
    manifest = json.loads((output_dir / "batch_manifest.json").read_text(encoding="utf-8"))
    assert len(manifest["records"]) == 3
