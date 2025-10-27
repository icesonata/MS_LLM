"""Cluster example dialogues into K clusters.

Primary embedding backend: sentence-transformers. If model download fails
(e.g., network timeout), falls back through several candidate model names.
If all Transformer models fail, gracefully degrades to a TF-IDF embedding so
that downstream pipeline can still function deterministically.
"""
import json
from pathlib import Path
import os
import numpy as np
from sklearn.cluster import KMeans

from sklearn.feature_extraction.text import TfidfVectorizer


def load_embedding_model(model_candidates=None, save_local: bool = True):
    """Attempt to load a SentenceTransformer model from a list of candidates.

    Returns an object with an `.encode(list[str]) -> np.ndarray` method. If all
    candidates fail, returns a TF-IDF based embedder implementing the same
    interface (fit-on-first-call behavior).

    Local caching behavior:
      - Looks for a previously saved model directory inside
        EMBEDDING_MODEL_LOCAL_DIR (env) or `<project_root>/models/embedding_cache/<sanitized_name>`
      - If found, loads from that directory.
      - If remote download succeeds and `save_local` is True, saves to the cache path.
    """
    backend = os.environ.get("EMBEDDING_BACKEND", "").lower()
    # if backend == "tfidf":
    #     # direct TF-IDF path
    #     class TfidfEmbedder:
    #         def __init__(self):
    #             self.vectorizer = TfidfVectorizer(max_features=2048)
    #             self.fitted = False
    #         def encode(self, texts, show_progress_bar=False):
    #             if not self.fitted:
    #                 mat = self.vectorizer.fit_transform(texts)
    #                 self.fitted = True
    #             else:
    #                 mat = self.vectorizer.transform(texts)
    #             return mat.toarray().astype("float32")
    #     print("[cluster_examples] Using TF-IDF backend (EMBEDDING_BACKEND=tfidf)")
    #     return TfidfEmbedder()

    if model_candidates is None:
        env_model = os.environ.get("EMBEDDING_MODEL")
        model_candidates = [
            env_model,
            "mixedbread-ai/mxbai-embed-large-v1",
            "sentence-transformers/all-MiniLM-L6-v2",
            "all-MiniLM-L6-v2",
            "sentence-transformers/paraphrase-MiniLM-L6-v2",
            "paraphrase-MiniLM-L6-v2",
        ]
    # Added: local cache root resolution
    project_root = Path(__file__).resolve().parents[1]
    cache_root = Path(os.environ.get("EMBEDDING_MODEL_LOCAL_DIR", project_root / "models" / "embedding_cache"))
    cache_root.mkdir(parents=True, exist_ok=True)

    # ensure timeouts are generous for HF hub
    os.environ.setdefault("HF_HUB_READ_TIMEOUT", "60")
    os.environ.setdefault("HF_HUB_CONNECT_TIMEOUT", "60")
    errors = []
    for name in [c for c in model_candidates if c]:
        safe_name = name.replace("/", "__")
        local_dir = cache_root / safe_name
        # Try local cached directory first
        if local_dir.exists():
            try:
                from sentence_transformers import SentenceTransformer  # local import
                print(f"[cluster_examples] Loading embedding model from local cache: {local_dir}")
                return SentenceTransformer(str(local_dir))
            except Exception as e:
                errors.append(f"local({local_dir}): {e}")

        try:
            from sentence_transformers import SentenceTransformer  # local import
            print(f"[cluster_examples] Downloading embedding model: {name}")
            model = SentenceTransformer(name)
            if save_local:
                try:
                    model.save(str(local_dir))
                    print(f"[cluster_examples] Saved embedding model locally to {local_dir}")
                except Exception as se:
                    print(f"[cluster_examples] Warning: failed to save model locally: {se}")
            return model
        except Exception as e:  # pragma: no cover - network dependent
            errors.append(f"{name}: {e}")
            continue

    # Fallback TF-IDF embedder
    # class TfidfEmbedder:
    #     def __init__(self):
    #         self.vectorizer = TfidfVectorizer(max_features=2048)
    #         self.fitted = False

    #     def encode(self, texts, show_progress_bar=False):  # mimic interface
    #         if not self.fitted:
    #             mat = self.vectorizer.fit_transform(texts)
    #             self.fitted = True
    #         else:
    #             mat = self.vectorizer.transform(texts)
    #         return mat.toarray().astype("float32")

    # print("[cluster_examples] All transformer model loads failed, using TF-IDF fallback. Errors:\n" + "\n".join(errors))
    # return TfidfEmbedder()

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "prepared_data" / "example_dialogues.jsonl"
OUT = ROOT / "prepared_data" / "clusters.json"


def load_examples(path: Path):
    items = []
    if not path.exists():
        return items
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                items.append(json.loads(line))
    return items


def main(k: int = 5):  
    items = load_examples(EXAMPLES)
    if not items:
        print("No example dialogues found at", EXAMPLES)
        return

    texts = [" ".join([t['text'] for t in it['dialogue']['turns']]) for it in items]
    model = load_embedding_model()
    embeds = model.encode(texts, show_progress_bar=True)

    kmeans = KMeans(n_clusters=min(k, len(texts)), random_state=42)
    labels = kmeans.fit_predict(embeds)

    clusters = {}
    for idx, lab in enumerate(labels):
        clusters.setdefault(int(lab), []).append({"index": idx, "dialogue": items[idx]['dialogue']})

    out = {"clusters": clusters, "cluster_centers": kmeans.cluster_centers_.tolist()}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
