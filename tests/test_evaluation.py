"""Test evaluation benchmark script against the 50 hand-labeled medical records."""

from pathlib import Path
from promptshield.evaluate import evaluate_dataset


def test_evaluate_50_medical_samples():
    dataset_path = Path("data/medical_eval_samples.json")
    assert dataset_path.exists(), "Evaluation dataset must exist"
    
    results = evaluate_dataset(str(dataset_path))
    overall = results["overall"]
    
    assert overall["tp"] > 400
    assert overall["fn"] == 0
    assert overall["precision"] >= 95.0
    assert overall["recall"] >= 95.0
    assert overall["f1"] >= 95.0
