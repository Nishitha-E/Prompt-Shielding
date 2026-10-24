import json
import time
from pathlib import Path
from typing import Dict, Any, List
from promptshield.redactor import PromptShieldEngine

class BatchProcessor:
    def __init__(self, engine=None):
        self.engine=engine or PromptShieldEngine(seed=42)

    def process_directory(self, input_dir, output_dir, session_file=None):
        inp=Path(input_dir)
        out=Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)

        if session_file and Path(session_file).exists():
            self.engine.load_session(session_file)

        files=sorted([f for f in inp.iterdir() if f.is_file() and f.suffix in [".txt", ".md", ".json"]])
        manifest_records=[]

        start_time=time.perf_counter()

        for file_path in files:
            t0=time.perf_counter()
            content=file_path.read_text(encoding="utf-8")
            sanitized=self.engine.redact(content)
            out_file=out / file_path.name
            out_file.write_text(sanitized, encoding="utf-8")
            elapsed_ms=(time.perf_counter() - t0) * 1000.0

            manifest_records.append({
                "filename": file_path.name,
                "input_chars": len(content),
                "output_chars": len(sanitized),
                "latency_ms": round(elapsed_ms, 2)
            })

        total_elapsed_ms=(time.perf_counter() - start_time) * 1000.0

        if session_file:
            self.engine.save_session(session_file)

        summary={
            "total_files": len(files),
            "total_pii_entities": len(self.engine.mapping),
            "total_elapsed_ms": round(total_elapsed_ms, 2),
            "records": manifest_records
        }

        manifest_path=out / "batch_manifest.json"
        manifest_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

        return summary
