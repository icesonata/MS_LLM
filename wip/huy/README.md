---
title: LLM Dialogue Evaluator
---

# LLM Dialogue Evaluator

Endâ€‘toâ€‘end pipeline to sample customer service dialogues, regenerate rubricâ€‘based scores with an LLM, cluster exemplar dialogues (Auto-CoT style), and perform fewâ€‘shot inference on a new dataset using the best example(s) per cluster.

## Features
- Sampling & initial evaluation with a rubric schema.
- Regeneration of perâ€‘metric scores (replacing legacy OverallExperience logic with weighted computation).
- Resilient embedding backend: Sentence-Transformers with automatic TFâ€‘IDF fallback (no network dependency required).
- K-Means clustering of exemplar dialogues for diversity.
- Fewâ€‘shot inference selecting the top similarity exemplar from each cluster, capped at 3 examples.
- Full rubric guidance automatically injected into prompts (no external prompt template required).
- Dryâ€‘run mode for prompt inspection without calling the API.

## Repository Structure
```
configs/
	rubrics.yaml              # Metrics, weights, guidance, JSON output schema
dataset/
	dialogues_CCPE.jsonl      # Source dataset for sampling examples
	dialogues_ReDial.jsonl    # Target dataset for final inference
prepared_data/              # Generated artifacts (ignored by git if large)
scripts/
	generate_samples.py       # Step 1: sample & initial evaluation
	regenerate_scores.py      # Step 2: re-score per metric (regenerated.json)
	cluster_examples.py       # Step 3: embedding + KMeans clustering
	inference_with_examples.py# Step 4: few-shot inference on target set
	evaluate_scores.py        # Step 5: quantitative evaluation of predictions
	llm_utils.py              # OpenAI client + key management helpers
```

## Installation
Python 3.11+ recommended.

```powershell
pip install -r requirements.txt
```

## OpenAI API Key
Set an environment variable (preferred):

```powershell
$env:OPENAI_API_KEY = "sk-..."  # PowerShell session only
```

Or place the key in `key.txt` (file is ignored by git) â€“ the code will fall back to it if the env var is absent. Do NOT commit secrets.

## Pipeline Steps

| Step | Script | Output | Description |
|------|--------|--------|-------------|
| 1 | `generate_samples.py` | `prepared_data/sampled_outputs.json` | Randomly sample (e.g., 20) dialogues from CCPE and get initial LLM evaluations per rubric schema. |
| 2 | `regenerate_scores.py` | `prepared_data/regenerated.json`, `prepared_data/example_dialogues.jsonl` | Reâ€‘prompt to regenerate perâ€‘metric scores & store normalized evaluation objects. |
| 3 | `cluster_examples.py` | `prepared_data/clusters.json` | Embed examples, run KMeans (default 5 clusters) with robust fallback. |
| 4 | `inference_with_examples.py` | `prepared_data/final_inference.json` | Build rubricâ€‘driven prompt + up to 3 best cluster exemplars for each target ReDial dialogue. |
| 5 | `evaluate_scores.py` | `prepared_data/eval_metrics.json`, optional `prepared_data/pred_vs_true.csv` | Compute regression / correlation metrics between model predicted OverallExperience and groundâ€‘truth scores. |

### Run All (Manual)
```powershell
python scripts/generate_samples.py
python scripts/regenerate_scores.py
python scripts/cluster_examples.py
python scripts/inference_with_examples.py
python scripts/evaluate_scores.py --input prepared_data/final_inference.json --out prepared_data/eval_metrics.json --csv prepared_data/pred_vs_true.csv
```

### Dry Run (Prompt Inspection)
Inspect the constructed prompt without an API call:
```powershell
$env:DRY_RUN = '1'; python scripts/inference_with_examples.py; Remove-Item Env:DRY_RUN
```

## Environment Variables
| Name | Purpose | Default |
|------|---------|---------|
| `OPENAI_API_KEY` | Auth for OpenAI API | (required) |
| `EMBEDDING_BACKEND` | `tfidf` to force TFâ€‘IDF; otherwise attempts sentence-transformers | (auto) |
| `EMBEDDING_MODEL` | Override model name for sentence-transformers | see code list |
| `DRY_RUN` | If `1`, stops after printing first prompt | 0 |
| `MAX_EXAMPLES` | Max few-shot exemplars inserted | 3 |
| `MAX_TARGETS` | Limit number of target dialogues processed | 50 |

## Rubric & Prompting
`rubrics.yaml` defines:
1. Metrics with `weight`, `desc`, and multi-band `guidance` text.
2. `format.output_schema` â†’ exact JSON structure required from the LLM.

Prompt assembly includes:
- High-level instructions.
- Metrics + weights summary.
- Full guidance per metric.
- JSON schema block (verbatim).
- Up to 3 few-shot exemplars (dialogue + evaluation JSON) chosen by highest cosine similarity per top clusters.
- Target dialogue and strict output instruction.

## Embeddings & Fallback Logic
1. Try configured sentence-transformers model(s) in priority order.
2. On failure/timeouts, auto-switch to TF-IDF vectorizer (scikit-learn) to ensure the pipeline still runs offline.

## Output Artifacts Summary
| File | Purpose |
|------|---------|
| `prepared_data/sampled_outputs.json` | Raw initial LLM evaluations for sampled CCPE examples |
| `prepared_data/regenerated.json` | Regenerated per-metric scores (clean structure) |
| `prepared_data/example_dialogues.jsonl` | Line-delimited examples with dialogue & evaluation JSON for clustering |
| `prepared_data/clusters.json` | Cluster assignments + dialogue indices |
| `prepared_data/final_inference.json` | Inference results on ReDial with examples_used references |
| `prepared_data/eval_metrics.json` | Summary evaluation metrics (MAE, RMSE, R2, correlations, bias) |
| `prepared_data/pred_vs_true.csv` | (Optional) Perâ€‘dialogue ground truth vs prediction comparison |

## Evaluation (Step 5)
After generating `final_inference.json`, you can quantify how well the model's predicted `OverallExperience.score` aligns with the groundâ€‘truth `score_total` by running:

```powershell
python scripts/evaluate_scores.py --input prepared_data/final_inference.json --out prepared_data/eval_metrics.json --csv prepared_data/pred_vs_true.csv
```

Metrics reported:
- MAE / MSE / RMSE / R2
- Pearson & Spearman correlations (with pâ€‘values if SciPy installed)
- Bias (mean(pred - true))
- MAPE (ignoring nearâ€‘zero denominators)

By default, evaluation normalizes both ground truth and predictions from 0â€‘100 to a 0â€‘5 scale (divide by 20) to match rubricâ€‘style banding. Adjust or remove this normalization inside `evaluate_scores.py` if you prefer native 0â€‘100 scale.

Artifacts:
- `eval_metrics.json` â€“ machineâ€‘readable metrics
- `pred_vs_true.csv` â€“ per dialogue comparison (only if `--csv` provided)

## Security & Secrets
- Never commit `key.txt` or raw API keys.
- Git push protection may block if a key appears. If you leak a key, revoke it immediately and rewrite history (or re-init).
- Add a pre-commit hook to scan staged diffs for `sk-` patterns if desired.

## Troubleshooting
| Issue | Cause | Fix |
|-------|-------|-----|
| Model download timeout | Network blocked for HuggingFace | Set `EMBEDDING_BACKEND=tfidf` |
| OpenAI auth error | Missing/invalid key | Export `OPENAI_API_KEY` or create `key.txt` (local) |
| Push rejected (secret) | Key in history | Rotate key, remove file, rewrite history, force push |
| Malformed JSON output | LLM drift | Add post-validation & retry (future enhancement) |

## Roadmap / Potential Enhancements
- JSON schema validator + automatic retry.
- Score consistency checker (e.g., recomputing weighted OverallExperience locally).
- Lightweight web UI to browse dialogues and evaluations.
- GitHub Action for nightly re-generation with updated rubric.

## License
Add a LICENSE file (MIT/Apache-2.0) if you plan to share publicly.

## Disclaimer
LLM-based scoring is heuristic; always human-audit critical evaluations.

---
Feel free to open issues or PRs to extend the pipeline.

A note on configs:
 - A GPT-4.1 specific configuration file is available at configs/config_gpt4_1.yaml.

