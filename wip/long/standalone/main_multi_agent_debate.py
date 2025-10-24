#!/usr/bin/env python3
"""
Simple Qwen self-consistency example.
Requires environment variable: QWEN_API_KEY
"""

import json
import os
import re
from collections import Counter
import openai  # uses OpenAI-compatible Qwen API endpoint
from typing import List, Any, Dict
from tqdm import tqdm
from prompts import *

MODEL = "qwen3-30b-a3b-instruct-2507"
BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
TEMPERATURE = 0.7
NUM_ITER = 1
# K = 5
MAX_TOKEN = 2048
SAMPLES_IDS = {335, 25, 26}

def extract_json_response(text):
    """
    Extract and parse the first valid JSON object from the model response.
    Handles extra text before/after JSON.
    """
    # Try to find a JSON object (naive but effective)
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None

def aggregate_scores(responses):
    """
    Aggregate scores per criterion using mode.
    Tie-breaker: choose higher score.
    """
    criteria = [
        "TaskSuccess",
        "Helpfulness",
        "Accuracy",
        "Understanding",
        "Empathy",
        "Fluency",
        "OverallExperience"
    ]
    
    result = {}
    
    for crit in criteria:
        scores = []
        justifications = []
        
        for resp in responses:
            if isinstance(resp, dict) and crit in resp:
                entry = resp[crit]
                if isinstance(entry, dict) and "score" in entry:
                    scores.append(entry["score"])
                    justifications.append(entry.get("justification", "No justification."))
        
        if not scores:
            result[crit] = {"score": 40, "justification": "No valid scores."}
            continue

        # Count frequencies
        freq = Counter(scores)
        max_count = max(freq.values())
        candidates = [s for s, c in freq.items() if c == max_count]
        
        if len(candidates) == 1:
            chosen = candidates[0]
        else:
            chosen = max(candidates)  # tie → higher score
        
        # Pick a matching justification
        for s, j in zip(scores, justifications):
            if s == chosen:
                justification = j
                break
        else:
            justification = "Aggregated."

        result[crit] = {"score": chosen, "justification": justification}
    
    return result

def load_dialogue_dataset(file_path: str) -> List[Dict[str, Any]]:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['dialogues']

def dialogue_to_prompt_format(dialogue: dict, include_overall: bool = False) -> str:
    lines = []
    
    # Process each turn
    for turn in dialogue['turns']:
        speaker = turn['speaker']
        text = turn['text'].replace('\t', ' ').replace('\n', ' ')  # Clean whitespace
        intent = turn['intent']
        
        if speaker == 'SYSTEM':
            # SYSTEM lines: speaker, text, intent (no scores)
            lines.append(f"SYSTEM\t{text}\t{intent}")
        else:  # USER
            if turn['scores'] is not None:
                # USER lines with scores: speaker, text, intent, scores_csv
                scores_csv = ','.join(map(str, turn['scores']))
                lines.append(f"USER\t{text}\t{intent}\t{scores_csv}")
            else:
                # USER lines without scores (rare, but possible)
                lines.append(f"USER\t{text}\t{intent}")
    
    # Only add OVERALL line if explicitly requested
    if include_overall and 'overall_scores' in dialogue and dialogue['overall_scores']:
        overall_csv = ','.join(map(str, dialogue['overall_scores']))
        lines.append(f"USER\tOVERALL\tOTHER\t{overall_csv}")
    
    return '\n'.join(lines)

def full_poc():
    dialogues = load_dialogue_dataset("selected_dialogues.json")
    summary_results = []      # For result.json (compact)
    detailed_results = {}     # For result_details.json (full breakdown)
    
    api_key = os.getenv("QWEN_API_KEY")
    if not api_key:
        raise ValueError("Please set QWEN_API_KEY environment variable.")
    client = openai.OpenAI(api_key=api_key, base_url=BASE_URL.strip())

    for dial in tqdm(dialogues, desc="Processing dialogues"):
        dialogue_id = dial["dialogue_id"]
        
        if dialogue_id in SAMPLES_IDS:
            print(f"Exclude sample dialogue (id={dialogue_id}) from evaluation")
            continue

        processed_dial = dialogue_to_prompt_format(dial, include_overall=False)

        valid_responses = []
        attempts = 0
        max_attempts = NUM_ITER + 5

        print(f"\nEvaluating dialogue {dialogue_id}...")

        while len(valid_responses) < NUM_ITER and attempts < max_attempts:
            try:
                resp = client.chat.completions.create(
                    model=MODEL,
                    messages=[
                        {"role": "system", "content": PROMPT_MULTI_AGENT_DEBATE},
                        {"role": "user", "content": processed_dial}
                    ],
                    temperature=TEMPERATURE,
                    max_tokens=MAX_TOKEN,
                    n=1,
                )
                raw = resp.choices[0].message.content.strip()
                parsed = extract_json_response(raw)
                
                if parsed:
                    valid_responses.append(parsed)
                    print(f"  ✅ Got valid response ({len(valid_responses)}/{NUM_ITER})")
                else:
                    print(f"  ❌ Invalid JSON (attempt {attempts + 1})")
                    
            except Exception as e:
                print(f"  ❌ API Error (attempt {attempts + 1}): {e}")
            
            attempts += 1

        # Initialize default result
        final_result = None
        model_score = None

        if valid_responses:
            final_result = aggregate_scores(valid_responses)
            model_score = final_result.get("OverallExperience", {}).get("score")

        # --- Save to compact summary (result.json) ---
        summary_results.append({
            "dialogue_id": dialogue_id,
            "average_score_100": dial.get("average_score_100", 0.0),
            "model_score": model_score
        })

        # --- Save full details (result_details.json) ---
        detailed_results[dialogue_id] = {
            "dialogue_id": dialogue_id,
            "ground_truth_100": dial.get("average_score_100", 0.0),
            "ground_truth_5": dial.get("average_score", 0.0),
            "model_evaluation": final_result  # This is the full dict with all categories
        }

        # Optional: save intermediate results
        with open("result_partial.json", "w") as f:
            json.dump(summary_results, f, indent=2)
        with open("result_details_partial.json", "w") as f:
            json.dump(detailed_results, f, indent=2)

    # Final save
    with open("result.json", "w") as f:
        json.dump(summary_results, f, indent=2)
    
    with open("result_details.json", "w") as f:
        json.dump(detailed_results, f, indent=2)
    
    print(f"\n✅ Evaluation complete!")
    print(f"   Summary saved to: result.json")
    print(f"   Full details saved to: result_details.json")
    print(f"   Total dialogues evaluated: {len(summary_results)}")

if __name__ == "__main__":
    # single_poc()
    full_poc()