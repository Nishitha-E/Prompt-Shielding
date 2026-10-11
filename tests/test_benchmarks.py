"""Test latency benchmark to verify sub-15ms typing threshold."""

from promptshield.benchmarks import run_latency_benchmark


def test_latency_performance_threshold():
    """Verify that P99 latency is strictly under 15ms per clinical document."""
    bench = run_latency_benchmark(iterations=2)
    assert bench["total_executions"] > 0
    # Mean latency should be well under 10ms
    assert bench["mean_latency_ms"] < 10.0, f"Mean latency {bench['mean_latency_ms']}ms exceeds 10ms"
    # P99 must be under 15ms so typing never lags
    assert bench["p99_latency_ms"] < 15.0, f"P99 latency {bench['p99_latency_ms']}ms exceeds 15ms"
    assert bench["typing_delay_imperceptible"] is True
    # Verhoeff should be capable of thousands of ops/sec
    assert bench["verhoeff_ops_per_sec"] > 5000
