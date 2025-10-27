"""Evaluate model prediction quality against ground truth scores.

Reads the `prepared_data/final_inference.json` file produced by
`inference_with_examples.py` and extracts:
  - Ground truth: dialogue.score_total
  - Prediction:  evaluation JSON -> OverallExperience.score (if present)

Outputs regression metrics:
  * Count
  * MAE, MSE, RMSE, R2
  * Pearson r (w/ p-value)
  * Spearman rho (w/ p-value)
  * Mean Absolute Percentage Error (safe variant ignoring zeros)
  * Bias (mean(pred - true))

By default prints a pretty table and writes a JSON summary to
`prepared_data/eval_metrics.json` (overwritable with --out).

Usage (PowerShell):
  python scripts/evaluate_scores.py \
      --input prepared_data/final_inference.json \
      --out prepared_data/eval_metrics.json

If you want CSV with per-dialogue comparison: add `--csv prepared_data/pred_vs_true.csv`.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import List, Dict, Any, Tuple

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
try:
    from scipy.stats import pearsonr, spearmanr  # Optional but common
except Exception:  # pragma: no cover
    pearsonr = spearmanr = None  # type: ignore


def load_items(path: Path) -> List[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Expected top-level list in final_inference.json")
    return data


def extract_scores(items: List[Dict[str, Any]]) -> Tuple[List[float], List[float], List[int]]:
    """Return (ground_truth, predictions, dialogue_ids) for valid records.

    Skips entries where either score is missing / malformed.
    """
    y_true: List[float] = []
    y_pred: List[float] = []
    ids: List[int] = []

    for entry in items:
        dialogue_obj = entry.get("dialogue", {})
        gt = dialogue_obj.get("score_total")  # ground truth 0-100 (float)
        # evaluation is stored as *string* of JSON typically
        eval_raw = entry.get("evaluation")
        predicted = None
        if isinstance(eval_raw, str):
            try:
                eval_json = json.loads(eval_raw)
            except json.JSONDecodeError:
                eval_json = {}
        elif isinstance(eval_raw, dict):
            eval_json = eval_raw
        else:
            eval_json = {}
        if isinstance(eval_json, dict):
            overall = eval_json.get("OverallExperience") or eval_json.get("overall_experience")
            if isinstance(overall, dict):
                predicted = overall.get("score")

        # Accept ints/floats only
        if (isinstance(gt, (int, float)) and isinstance(predicted, (int, float))):
            # Normalize to float
            try:
                gt_f = float(gt)
                pred_f = float(predicted)
            except Exception:  # pragma: no cover
                continue
            # Skip NaNs
            if math.isnan(gt_f) or math.isnan(pred_f):
                continue
            y_true.append(gt_f)
            y_pred.append(pred_f)
            # Dialogue id may not always exist or be int
            did = dialogue_obj.get("dialogue_id")
            ids.append(int(did) if isinstance(did, (int, float)) else -1)

    return y_true, y_pred, ids


def safe_mape(y_true: List[float], y_pred: List[float]) -> float:
    eps = 1e-8
    pct = []
    for t, p in zip(y_true, y_pred):
        if abs(t) < eps:  # skip zero or near-zero to avoid explosion
            continue
        pct.append(abs(p - t) / abs(t))
    if not pct:
        return float("nan")
    return float(np.mean(pct) * 100.0)


def compute_metrics(y_true: List[float], y_pred: List[float]) -> Dict[str, Any]:
    if not y_true:
        return {"count": 0}
    yt = np.array(y_true)
    yp = np.array(y_pred)

    mae = mean_absolute_error(yt, yp)
    mse = mean_squared_error(yt, yp)
    rmse = math.sqrt(mse)
    r2 = r2_score(yt, yp)
    bias = float(np.mean(yp - yt))
    mape = safe_mape(y_true, y_pred)

    metrics: Dict[str, Any] = {
        "count": len(y_true),
        "MAE": mae,
        "MSE": mse,
        "RMSE": rmse,
        "R2": r2,
        "Bias": bias,  # positive => overestimation
        "MAPE_percent": mape,
    }

    if pearsonr and len(y_true) > 1:
        pr, p_p = pearsonr(yt, yp)
        metrics["PearsonR"] = float(pr)
        metrics["PearsonR_p"] = float(p_p)
    if spearmanr and len(y_true) > 1:
        sr, s_p = spearmanr(yt, yp)
        metrics["SpearmanRho"] = float(sr)
        metrics["SpearmanRho_p"] = float(s_p)
    return metrics


def pretty_print(metrics: Dict[str, Any]):
    if not metrics.get("count"):
        print("No valid records.")
        return
    order = [
        "count","MAE","MSE","RMSE","R2","Bias","MAPE_percent","PearsonR","PearsonR_p","SpearmanRho","SpearmanRho_p",
        "MeanInferenceSeconds","MedianInferenceSeconds","P95InferenceSeconds","TotalInferenceSeconds"
    ]
    print("\nEvaluation Metrics")
    print("------------------")
    for k in order:
        if k in metrics:
            print(f"{k:15s}: {metrics[k]:.6f}" if isinstance(metrics[k], (int, float)) else f"{k:15s}: {metrics[k]}")


def write_csv(path: Path, ids: List[int], y_true: List[float], y_pred: List[float]):
    import csv
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["dialogue_id","score_total","predicted_overall_experience"])
        for did, t, p in zip(ids, y_true, y_pred):
            w.writerow([did, f"{t:.4f}", f"{p:.4f}"])


def main():
    parser = argparse.ArgumentParser(description="Evaluate predicted OverallExperience scores against ground truth score_total.")
    parser.add_argument("--input", default="prepared_data/final_inference.json", help="Path to final_inference.json")
    parser.add_argument("--out", default="prepared_data/eval_metrics.json", help="Path to write metrics JSON")
    parser.add_argument("--csv", default=None, help="Optional path to write per-dialogue CSV")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")

    items = load_items(input_path)
    y_true, y_pred, ids = extract_scores(items)
    y_true = [x / 20 for x in y_true]  # normalize to 0-5
    y_pred = [x / 20 for x in y_pred]  # normalize to 0-5

    metrics = compute_metrics(y_true, y_pred)

    # Aggregate inference time stats if present
    inference_times = []
    for entry in items:
        t = entry.get("inference_seconds")
        if isinstance(t, (int, float)):
            try:
                tf = float(t)
            except Exception:
                continue
            if not math.isnan(tf):
                inference_times.append(tf)
    if inference_times:
        metrics["MeanInferenceSeconds"] = float(np.mean(inference_times))
        metrics["MedianInferenceSeconds"] = float(np.median(inference_times))
        metrics["P95InferenceSeconds"] = float(np.percentile(inference_times, 95))
        metrics["TotalInferenceSeconds"] = float(np.sum(inference_times))

    # ensure output dir
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    pretty_print(metrics)

    if args.csv:
        csv_path = Path(args.csv)
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        write_csv(csv_path, ids, y_true, y_pred)
        print(f"Per-dialogue CSV written to {csv_path}")

    print(f"Metrics JSON written to {out_path}")


if __name__ == "__main__":  # pragma: no cover
    main()
