"""Latency and throughput performance benchmarking for Prompt Shield.

Fulfills qualification requirement:
'Latency low enough that typing never feels delayed.' (Target: < 15ms per prompt)
"""

import time
import json
import statistics
from typing import Dict, Any, List
from pathlib import Path
from promptshield.redactor import PromptShieldEngine
from promptshield.verhoeff import validate_verhoeff, generate_verhoeff_number


def run_latency_benchmark(dataset_path: str = "data/medical_eval_samples.json", iterations: int = 5) -> Dict[str, Any]:
    """Benchmark end-to-end redaction latency across clinical documents."""
    with open(dataset_path, "r", encoding="utf-8") as f:
        samples = json.load(f)

    engine = PromptShieldEngine(seed=42)
    latencies_ms: List[float] = []
    total_chars = 0
    total_words = 0

    # Warmup
    for s in samples[:5]:
        engine.redact(s["text"])

    # Measured runs
    start_total = time.perf_counter()
    for _ in range(iterations):
        for s in samples:
            text = s["text"]
            t0 = time.perf_counter()
            _ = engine.redact(text)
            t1 = time.perf_counter()

            latencies_ms.append((t1 - t0) * 1000.0)
            total_chars += len(text)
            total_words += len(text.split())
    total_time = time.perf_counter() - start_total

    latencies_ms.sort()
    count = len(latencies_ms)

    p50 = statistics.median(latencies_ms)
    p95 = latencies_ms[int(0.95 * count)]
    p99 = latencies_ms[int(0.99 * count)]
    mean_lat = statistics.mean(latencies_ms)

    chars_per_sec = total_chars / total_time if total_time > 0 else 0
    words_per_sec = total_words / total_time if total_time > 0 else 0

    # Checksum throughput test
    sample_aadhaar = generate_verhoeff_number("23635412891")
    ck_count = 10000
    ck_start = time.perf_counter()
    for _ in range(ck_count):
        validate_verhoeff(sample_aadhaar)
    ck_time = time.perf_counter() - ck_start
    verhoeff_ops_per_sec = ck_count / ck_time if ck_time > 0 else 0

    return {
        "samples_evaluated": len(samples),
        "total_executions": count,
        "mean_latency_ms": round(mean_lat, 3),
        "p50_latency_ms": round(p50, 3),
        "p95_latency_ms": round(p95, 3),
        "p99_latency_ms": round(p99, 3),
        "chars_per_sec": int(chars_per_sec),
        "words_per_sec": int(words_per_sec),
        "verhoeff_ops_per_sec": int(verhoeff_ops_per_sec),
        "typing_delay_imperceptible": p99 < 15.0,
    }


def print_benchmark_report(bench: Dict[str, Any]) -> None:
    """Print formatted performance benchmark table."""
    print("=" * 65)
    print(" PROMPT SHIELD: LATENCY & PERFORMANCE PROFILE")
    print("=" * 65)
    print(f"Total Test Executions    : {bench['total_executions']}")
    print(f"Mean Redaction Latency   : {bench['mean_latency_ms']} ms")
    print(f"P50 (Median) Latency     : {bench['p50_latency_ms']} ms")
    print(f"P95 Latency              : {bench['p95_latency_ms']} ms")
    print(f"P99 Latency              : {bench['p99_latency_ms']} ms")
    print("-" * 65)
    print(f"Throughput (Characters)  : {bench['chars_per_sec']:,} chars/sec")
    print(f"Throughput (Words)       : {bench['words_per_sec']:,} words/sec")
    print(f"Verhoeff Checksum Speed  : {bench['verhoeff_ops_per_sec']:,} checks/sec")
    print("-" * 65)
    status = "PASSED (< 15ms target)" if bench["typing_delay_imperceptible"] else "WARNING"
    print(f"Typing Delay Check (<15ms): [{status}]")
    print("=" * 65)


if __name__ == "__main__":
    b = run_latency_benchmark()
    print_benchmark_report(b)
