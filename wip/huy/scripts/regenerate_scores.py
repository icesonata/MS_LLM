"""Read prepared_data/sampled_outputs.json, replace OverallExperience by score_total
and ask LLM to generate per-metric scores matching rubric. Writes prepared_data/regenerated.json
and saves an examples file prepared_data/example_dialogues.jsonl for later clustering.
"""
import os
import json
from pathlib import Path
import yaml

from scripts.llm_utils import simple_user_prompt

ROOT = Path(__file__).resolve().parents[1]
IN = ROOT / "prepared_data" / "sampled_outputs.json"
OUT = ROOT / "prepared_data" / "regenerated.json"
EXAMPLES = ROOT / "prepared_data" / "example_dialogues.jsonl"
RUBRIC = ROOT / "configs" / "rubrics.yaml"


def load_rubric(rubric_path: Path):
    with open(rubric_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def call_openai(prompt: str, temperature: float = 0.0):
    return simple_user_prompt(prompt, temperature=temperature, max_tokens=800)


def main():
    cfg = load_rubric(RUBRIC)
    with open(IN, "r", encoding="utf-8") as f:
        items = json.load(f)

    template = Path(ROOT / "configs" / "prompt_template.txt").read_text(encoding="utf-8")
    outputs = []
    EXAMPLES.parent.mkdir(parents=True, exist_ok=True)

    for entry in items:
        dialogue = entry.get("dialogue")
        # prefer existing score_total if present, else fallback
        score_total = dialogue.get("score_total") or dialogue.get("score", None) or None
        if score_total is None:
            # if evaluation contains OverallExperience, try to parse it
            score_total = None

        # create a prompt that asks for per-criteria scores that sum/aggregate to score_total
        dialogue_text = "\n".join([f"{t['role']}: {t['text']}" for t in dialogue.get("turns", [])])
        prompt = template.replace("{dialogue_transcript}", dialogue_text).replace("{example}", "")
        prompt += f"\n\nNOTE: The original dataset has score_total: {score_total}. Produce JSON with the seven metrics and OverallExperience that aligns (rounded) with this score_total. Use integer scores and one-sentence justification each."

        try:
            resp = call_openai(prompt)
        except Exception as e:
            resp = json.dumps({"error": str(e)})

        outputs.append({"dialogue": dialogue, "regenerated_evaluation": resp})

        # also save example dialogue for clustering
        with open(EXAMPLES, "a", encoding="utf-8") as exf:
            exf.write(json.dumps({"dialogue": dialogue, "evaluation": resp}, ensure_ascii=False) + "\n")

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(outputs, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
