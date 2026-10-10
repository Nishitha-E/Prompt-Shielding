"""Evaluation script for calculating Precision, Recall, and F1 score against hand-labeled medical evaluation dataset."""

import json
from pathlib import Path
from typing import Dict, List, Any
from promptshield.detectors import PIIDetector


def evaluate_dataset(dataset_path: str) -> Dict[str, Any]:
    """Run evaluation on labeled dataset and compute Precision, Recall, and F1."""
    with open(dataset_path, "r", encoding="utf-8") as f:
        samples = json.load(f)

    detector = PIIDetector(seed=42)

    stats: Dict[str, Dict[str, int]] = {}

    def get_stat_bucket(pii_type: str) -> Dict[str, int]:
        if pii_type not in stats:
            stats[pii_type] = {"tp": 0, "fp": 0, "fn": 0}
        return stats[pii_type]

    for sample in samples:
        text = sample["text"]
        ground_truth = sample.get("entities", [])
        detected_matches = detector.detect_all(text)

        # Normalize ground truth: list of (type, value)
        gt_items = [(e["type"], e["value"].strip()) for e in ground_truth]
        pred_items = [(m.pii_type, m.original.strip()) for m in detected_matches]

        matched_gt = set()
        matched_pred = set()

        # Find True Positives
        for p_idx, (p_type, p_val) in enumerate(pred_items):
            for g_idx, (g_type, g_val) in enumerate(gt_items):
                if g_idx not in matched_gt and p_idx not in matched_pred:
                    # Match if types match and values match (or substring match for names with titles)
                    if p_type == g_type and (p_val == g_val or g_val in p_val or p_val in g_val):
                        bucket = get_stat_bucket(g_type)
                        bucket["tp"] += 1
                        matched_gt.add(g_idx)
                        matched_pred.add(p_idx)
                        break

        # False Positives (predictions with no matching ground truth)
        for p_idx, (p_type, p_val) in enumerate(pred_items):
            if p_idx not in matched_pred:
                bucket = get_stat_bucket(p_type)
                bucket["fp"] += 1

        # False Negatives (ground truth items missed)
        for g_idx, (g_type, g_val) in enumerate(gt_items):
            if g_idx not in matched_gt:
                bucket = get_stat_bucket(g_type)
                bucket["fn"] += 1

    # Compute metrics
    results: Dict[str, Any] = {"per_type": {}, "overall": {}}
    total_tp = sum(b["tp"] for b in stats.values())
    total_fp = sum(b["fp"] for b in stats.values())
    total_fn = sum(b["fn"] for b in stats.values())

    for pii_type, b in sorted(stats.items()):
        tp, fp, fn = b["tp"], b["fp"], b["fn"]
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
        results["per_type"][pii_type] = {
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "precision": round(prec * 100, 2),
            "recall": round(rec * 100, 2),
            "f1": round(f1 * 100, 2),
        }

    overall_prec = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
    overall_rec = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
    overall_f1 = (2 * overall_prec * overall_rec) / (overall_prec + overall_rec) if (overall_prec + overall_rec) > 0 else 0.0

    results["overall"] = {
        "tp": total_tp,
        "fp": total_fp,
        "fn": total_fn,
        "precision": round(overall_prec * 100, 2),
        "recall": round(overall_rec * 100, 2),
        "f1": round(overall_f1 * 100, 2),
    }

    return results


def print_evaluation_report(results: Dict[str, Any]):
    """Print formatted evaluation report table."""
    print("=" * 75)
    print(" PROMPT SHIELD EVALUATION BENCHMARK: HEALTHCARE CLINICAL PII")
    print("=" * 75)
    print(f"{'Identifier Type':<20} | {'TP':<5} | {'FP':<5} | {'FN':<5} | {'Precision':<10} | {'Recall':<8} | {'F1':<8}")
    print("-" * 75)
    for pii_type, m in results["per_type"].items():
        print(
            f"{pii_type:<20} | {m['tp']:<5} | {m['fp']:<5} | {m['fn']:<5} | "
            f"{m['precision']:>8.2f}% | {m['recall']:>6.2f}% | {m['f1']:>6.2f}%"
        )
    print("-" * 75)
    ov = results["overall"]
    print(
        f"{'OVERALL':<20} | {ov['tp']:<5} | {ov['fp']:<5} | {ov['fn']:<5} | "
        f"{ov['precision']:>8.2f}% | {ov['recall']:>6.2f}% | {ov['f1']:>6.2f}%"
    )
    print("=" * 75)


if __name__ == "__main__":
    import sys
    dataset_file = sys.argv[1] if len(sys.argv) > 1 else "data/medical_eval_samples.json"
    res = evaluate_dataset(dataset_file)
    print_evaluation_report(res)
