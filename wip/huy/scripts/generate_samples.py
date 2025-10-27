"""Sample dialogues from dialogues_ReDial.jsonl, prompt the OpenAI API to evaluate
using rubric format from configs/rubrics.yaml and save to prepared_data/sampled_outputs.json

Writes 20 samples by default. Uses OPENAI_API_KEY from environment (get_key.py sets it).
"""
import os
import json
import random
from pathlib import Path

import yaml

from scripts.llm_utils import simple_user_prompt

ROOT = Path(__file__).resolve().parents[1]
# DATA = ROOT / "dataset" / "dialogues_ReDial.jsonl"
DATA = ROOT / "dataset" / "dialogues_CCPE.jsonl"
EXCLUDE_TEST_DATA = ROOT / "dataset" / "formatted_selected_dialogues.jsonl"
RUBRIC = ROOT / "configs" / "rubrics.yaml"
OUT = ROOT / "prepared_data" / "sampled_outputs.json"


def load_rubric_output_schema(rubric_path: Path):
    with open(rubric_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    return cfg["format"]["output_schema"], cfg


def read_jsonl(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def call_openai(prompt: str, temperature: float = 0.0):
    return simple_user_prompt(prompt, temperature=temperature, max_tokens=800)


def main(sample_n: int = 50):
    schema_text, cfg = load_rubric_output_schema(RUBRIC)
    dialogues = list(read_jsonl(DATA))
    sampled = random.sample(dialogues, min(sample_n, len(dialogues)))
    if EXCLUDE_TEST_DATA.exists():
        test_dialogues = {d["dialogue_id"] for d in read_jsonl(EXCLUDE_TEST_DATA)}
        filtered_dialogues = [d for d in dialogues if d.get("dialogue_id") not in test_dialogues]
        sampled = random.sample(filtered_dialogues, min(sample_n, len(filtered_dialogues)))
        
    outputs = []
    template = Path(ROOT / "configs" / "prompt_template.txt").read_text(encoding="utf-8")

    for item in sampled:
        dialogue_text = "\n".join([f"{t['role']}: {t['text']}" for t in item.get("turns", [])])
        prompt = template.replace("{dialogue_transcript}", dialogue_text).replace("{example}", "")
        prompt = prompt + "\n\nPlease respond using this JSON schema exactly:\n" + schema_text
        try:
            resp = call_openai(prompt)
        except Exception as e:
            resp = json.dumps({"error": str(e)})

        outputs.append({"dialogue": item, "evaluation": resp})

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(outputs, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
