"""Inference pipeline with resilient embedding backend.

Attempts to load a sentence-transformers model (multiple fallbacks). If all
fail due to connectivity, uses TF-IDF embeddings so the evaluation still runs.
"""
import os
import json
from pathlib import Path
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from scripts.llm_utils import simple_user_prompt
import yaml
import time  # added for per-dialogue timing
# progress bar (safe fallback)
try:
    from tqdm import tqdm
except ImportError:  # minimal fallback
    def tqdm(x, *args, **kwargs):
        return x

ROOT = Path(__file__).resolve().parents[1]
REVAL = ROOT / "dataset" / "formatted_selected_dialogues.jsonl"
CLUSTERS = ROOT / "prepared_data" / "clusters.json"
EXAMPLES_PATH = ROOT / "prepared_data" / "example_dialogues.jsonl"
OUT = ROOT / "prepared_data" / "final_inference.json"
RUBRIC_PATH = ROOT / "configs" / "rubrics.yaml"


def load_embedding_model():
    os.environ.setdefault("HF_HUB_READ_TIMEOUT", "60")
    os.environ.setdefault("HF_HUB_CONNECT_TIMEOUT", "60")
    backend = os.environ.get("EMBEDDING_BACKEND", "").lower()
    if backend == "tfidf":
        class TfidfEmbedder:
            def __init__(self):
                self.vec = TfidfVectorizer(max_features=2048)
                self.fit = False
            def encode(self, texts, show_progress_bar=False):
                if not self.fit:
                    m = self.vec.fit_transform(texts)
                    self.fit = True
                else:
                    m = self.vec.transform(texts)
                return m.toarray().astype("float32")
        print("[inference] Using TF-IDF backend (EMBEDDING_BACKEND=tfidf)")
        return TfidfEmbedder()

    candidates = [
        os.environ.get("EMBEDDING_MODEL"),
        "sentence-transformers/all-MiniLM-L6-v2",
        "all-MiniLM-L6-v2",
        "sentence-transformers/paraphrase-MiniLM-L6-v2",
        "paraphrase-MiniLM-L6-v2",
    ]
    errs = []

    for name in [c for c in candidates if c]:
        try:
            from sentence_transformers import SentenceTransformer  # local import
            return SentenceTransformer(name)
        except Exception as e:  # pragma: no cover
            errs.append(f"{name}: {e}")
    # TF-IDF fallback
    class TfidfEmbedder:
        def __init__(self):
            self.vec = TfidfVectorizer(max_features=2048)
            self.fit = False
        def encode(self, texts, show_progress_bar=False):
            if not self.fit:
                m = self.vec.fit_transform(texts)
                self.fit = True
            else:
                m = self.vec.transform(texts)
            return m.toarray().astype("float32")
    print("[inference] Transformer model load failed, using TF-IDF fallback. Errors:\n" + "\n".join(errs))
    return TfidfEmbedder()


def load_jsonl(p: Path):
    out = []
    with open(p, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                out.append(json.loads(line))
    return out


def call_openai(prompt: str, temperature: float = 0.0):
    return simple_user_prompt(prompt, temperature=temperature, max_tokens=800)


def main(n_examples_per_cluster: int = 1, top_k_clusters: int = 5):
    clusters_doc = json.load(open(CLUSTERS, "r", encoding="utf-8"))
    # Load rubric to include schema & short guidance in prompt header
    try:
        with open(RUBRIC_PATH, 'r', encoding='utf-8') as rf:
            rubric_cfg = yaml.safe_load(rf)
        output_schema = rubric_cfg.get('format', {}).get('output_schema', '').strip()
        # Build a compact criteria summary
        criteria = rubric_cfg.get('metrics', rubric_cfg)
    except Exception:
        rubric_cfg = {}
        output_schema = ''
        criteria = {}
    example_items = load_jsonl(EXAMPLES_PATH)
    model = load_embedding_model()

    # prepare cluster example texts and embeddings (now include evaluation JSON if available)
    cluster_examples = []
    for cid, members in clusters_doc["clusters"].items():
        for m in members:
            turns = m['dialogue']['turns']
            text = "\n".join([t['role']+': '+t['text'] for t in turns])
            # retrieve evaluation / regenerated_evaluation from original example_items by index
            evaluation_text = None
            idx = m.get('index')
            if idx is not None and 0 <= idx < len(example_items):
                source = example_items[idx]
                # regeneration file saved as 'evaluation'; regenerated.json uses 'regenerated_evaluation'
                evaluation_text = source.get('regenerated_evaluation') or source.get('evaluation')
            cluster_examples.append({
                "cluster": int(cid),
                "text": text,
                "dialogue": m['dialogue'],
                "evaluation": evaluation_text,
            })

    example_texts = [c['text'] for c in cluster_examples]
    ex_emb = model.encode(example_texts, show_progress_bar=False)

    # process target dialogues
    targets = load_jsonl(REVAL)
    out = []

    # wrap targets with tqdm for a progress bar
    for tgt in tqdm(targets[:], desc="Inference", total=len(targets), unit="dlg"):
        # add timer here if desired
        start_time = time.perf_counter()
        
        tgt_text = " ".join([t['text'] for t in tgt['turns']])
        tgt_emb = model.encode([tgt_text])[0]

        # find best example per cluster
        best_per_cluster = {}
        sims = cosine_similarity([tgt_emb], ex_emb)[0]
        for idx, sim in enumerate(sims):
            cid = cluster_examples[idx]['cluster']
            if cid not in best_per_cluster or sim > best_per_cluster[cid]['sim']:
                best_per_cluster[cid] = {"sim": float(sim), "example": cluster_examples[idx]}

        # select top_k clusters by sim
        chosen = sorted(best_per_cluster.values(), key=lambda x: x['sim'], reverse=True)[:top_k_clusters]
        # limit final examples to max_examples (default 3)
        max_examples = int(os.environ.get("MAX_EXAMPLES", "3"))
        if len(chosen) > max_examples:
            chosen = chosen[:max_examples]

        # --- Prompt standardization (rubric-only, no external template) ---
        def build_prompt():
            # 1. High-level instruction
            base = (
                "You are an evaluator for customer service dialogues."
                "Use the provided few-shot examples as guidance."
                "For the target dialogue, produce a JSON object with six criteria scores (discrete values: 20, 40, 60, 80, 100) and a one-sentence justification for each criterion."
                "Also include \"OverallExperience\", which represents the average of all six criteria scores."
                "After averaging, round the result down to the nearest discrete value (for example, an overall score of 90 should be scaled down to 80; 79 would also map to 60)."
                "Use only evidence explicitly found in the dialogue when providing justifications."

            )

            # 2. Metrics summary block with weight & short desc
            metrics_block_lines = ["=== Metrics & Weights ==="]
            rub_metrics = rubric_cfg.get('metrics', {}) if rubric_cfg else {}
            for name, mcfg in rub_metrics.items():
                wt = mcfg.get('weight', '?')
                desc = mcfg.get('desc', '').replace('\n', ' ')
                metrics_block_lines.append(f"- {name} (w={wt}): {desc}")
            metrics_block = "\n".join(metrics_block_lines)

            # 3. Full guidance block per metric
            guidance_lines = ["=== Full Guidance (All bands per metric) ==="]
            for name, mcfg in rub_metrics.items():
                g = mcfg.get('guidance', '').strip()
                if g:
                    guidance_lines.append(f"{name} guidance:\n{g}")
            guidance_block = "\n\n".join(guidance_lines)

            # 4. Output schema
            schema_block = "=== Output JSON Schema ===\n" + (output_schema or '')

            # 5. Few-shot examples
            example_blocks = []
            for c in chosen:
                ex = c['example']
                eval_json = ex.get('evaluation')
                ex_header = "--- Few-Shot Example ---"
                ex_dialogue = ex['text']
                if eval_json:
                    example_blocks.append(f"{ex_header}\nDialogue:\n{ex_dialogue}\nEvaluation JSON:\n{eval_json}")
                else:
                    example_blocks.append(f"{ex_header}\nDialogue:\n{ex_dialogue}")
            examples_section = "\n\n".join(example_blocks)

            # 6. Target dialogue
            target_section = "=== Target Dialogue To Evaluate ===\n" + "\n".join([f"{t['role']}: {t['text']}" for t in tgt['turns']])

            # 7. Final instruction for output
            final_instruction = (
                # "Produce ONLY a single JSON object matching the schema. "
                # "Scores must be integers 0-100. Justification: one concise sentence each. "
                # "OverallExperience = weighted mean (weights above), rounded to nearest integer."
                "You must apply the EXACT BAREM below. Do not invent extra rules. Use only text from the dialogue as evidence. Scores must be one of {20,40,60,80,100}. For \"OverallExperience\" compute a weighted average using weights:"
                "TaskSuccess 0.40, Helpfulness 0.15, Accuracy 0.15, Understanding 0.10, Empathy 0.10, Fluency 0.10 — then map the resulting value to the nearest discrete bucket {20,40,60,80,100}."


            )

            return "\n\n".join([
                base,
                metrics_block,
                guidance_block,
                schema_block,
                examples_section,
                target_section,
                final_instruction,
            ])

        prompt = build_prompt()
       
        try:
            resp = call_openai(prompt)
        except Exception as e:
            resp = json.dumps({"error": str(e)})
        
        elapsed = time.perf_counter() - start_time  # compute inference duration

        out.append({
            "dialogue": tgt,
            "evaluation": resp,
            "examples_used": [c['example']['dialogue'] for c in chosen],
            "inference_seconds": elapsed
        })

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
