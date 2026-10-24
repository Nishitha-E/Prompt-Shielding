"""Test evaluation benchmark script against the 50 hand-labeled education records."""

from pathlib import Path
from promptshield.evaluate import evaluate_dataset


def test_evaluate_50_education_samples():
    dataset_path = Path("data/education_eval_samples.json")
    assert dataset_path.exists(), "Evaluation dataset must exist"

    results = evaluate_dataset(str(dataset_path))
    overall = results["overall"]

    assert overall["tp"] >= 500
    assert overall["fn"] <= 10
    assert overall["precision"] >= 95.0
    assert overall["recall"] >= 95.0
    assert overall["f1"] >= 95.0
