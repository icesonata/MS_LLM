import json
import os
from typing import Dict, Any, List
import google.generativeai as genai

genai.configure(api_key='...')  # Replace with your API key
model = genai.GenerativeModel('gemini-2.0-flash')  


# Step 1: Read the Barem prompt from file
def read_barem_prompt(file_path: str) -> str:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} not found.")
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

# Step 2: Read dialogues from JSON
def read_dialogues(file_path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} not found.")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    dialogues = data.get('dialogues', [])
    if not dialogues:
        raise ValueError("No 'dialogues' key found in JSON.")
    result = []
    for dlg in dialogues:
        dlg_id = dlg.get('dialogue_id')
        if dlg_id is None:
            raise ValueError(f"Missing 'dialogue_id' in dialogue: {dlg}")
        avg_score = dlg.get('average_score')
        if avg_score is None:
            raise ValueError(f"Missing 'average_score' in dialogue_id {dlg_id}")
        turns = dlg.get('turns', [])
        overall_scores = dlg.get('overall_scores', [])
        result.append({
            'dialogue_id': dlg_id,
            'average_score': avg_score,
            'turns': turns,
            'overall_scores': overall_scores
        })
    return sorted(result, key=lambda x: x['dialogue_id'])  # Sort early for consistency

# Step 3: Format a single dialogue transcript like in barem examples
def format_transcript(dlg: Dict[str, Any]) -> str:
    lines = []
    for turn in dlg['turns']:
        speaker = turn.get('speaker', '').upper()
        text = turn.get('text', '').strip()
        intent = turn.get('intent') or 'OTHER'
        scores = turn.get('scores')
        line = f"{speaker} {text} {intent}"
        if scores:
            line += f" {','.join(map(str, scores))}"
        lines.append(line)
    # Add overall line if present
    if dlg['overall_scores']:
        overall_line = f"USER OVERALL OTHER {','.join(map(str, dlg['overall_scores']))}"
        lines.append(overall_line)
    return '\n'.join(lines)

# Step 4: Format batch for prompt
def format_batch(batch: List[Dict[str, Any]]) -> str:
    formatted = []
    for dlg in batch:
        transcript = format_transcript(dlg)
        formatted.append(f"Dialogue ID: {dlg['dialogue_id']}\n{transcript}\n{'=' * 80}")
    return '\n\n'.join(formatted)

# Step 5: Call Gemini with prompt + batch
def call_gemini(barem_prompt: str, batch_text: str) -> str:
    # Remove the {{dialogue_transcript}} placeholder and add instructions for multiple
    prompt_base = barem_prompt.replace('{{dialogue_transcript}}', '[MULTIPLE DIALOGUES HERE]')
    full_prompt = (
        prompt_base +
        "\n\nNow, evaluate MULTIPLE dialogues below. For each, apply the exact same BAREM and output format."
        "\nOutput ONLY a strict JSON array of objects, one per dialogue, in order of appearance."
        "\nEach object must include 'dialogue_id' matching the Dialogue ID provided, followed by the JSON structure as specified in OUTPUT FORMAT."
        "\nDo not add any text outside the JSON array."
        f"\n\n{batch_text}"
    )
    response = model.generate_content(full_prompt)
    return response.text.strip()

# Step 6: Parse Gemini response - clean and load as list of dicts
def parse_response(response_text: str) -> List[Dict[str, Any]]:
    # Clean common wrappers
    if response_text.startswith('```json'):
        response_text = response_text[7:].strip()
    if response_text.endswith('```'):
        response_text = response_text[:-3].strip()
    try:
        parsed = json.loads(response_text)
        if not isinstance(parsed, list):
            raise ValueError("Response is not a JSON array.")
        return parsed
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {e}\nResponse: {response_text}")

# Step 7: Extract model_score
def extract_model_score(full_result: Dict[str, Any]) -> int:
    return full_result.get('OverallExperience', {}).get('score', 0)

# Main execution
def main():
    barem_file = 'barem.txt'
    dialogues_file = 'selected_dialogues.json'
    batch_size = 10

    # Read files
    barem_prompt = read_barem_prompt(barem_file)
    all_dialogues = read_dialogues(dialogues_file)
    print(f"Loaded {len(all_dialogues)} dialogues.")

    if len(all_dialogues) != 38:
        print(f"Warning: Expected 38 dialogues, loaded {len(all_dialogues)}.")

    # Process in batches
    all_full_results = []
    all_summary = []

    for i in range(0, len(all_dialogues), batch_size):
        batch = all_dialogues[i:i + batch_size]
        batch_ids = [d['dialogue_id'] for d in batch]
        batch_text = format_batch(batch)

        # Call API
        response_text = call_gemini(barem_prompt, batch_text)
        print(f"Batch {i//batch_size + 1} (IDs {batch_ids[0]}-{batch_ids[-1]}): response length {len(response_text)}")

        # Parse
        batch_results = parse_response(response_text)
        if len(batch_results) != len(batch):
            raise ValueError(f"Parsed {len(batch_results)} results, but batch has {len(batch)} dialogues.")

        for j, full_result in enumerate(batch_results):
            dlg = batch[j]
            # Ensure dialogue_id is included
            full_result['dialogue_id'] = dlg['dialogue_id']
            model_score = extract_model_score(full_result)
            all_summary.append({
                "dialogue_id": dlg['dialogue_id'],
                "average_score": dlg['average_score'],
                "model_score": model_score
            })
            all_full_results.append(full_result)

    # Sort by dialogue_id
    all_summary.sort(key=lambda x: x['dialogue_id'])
    all_full_results.sort(key=lambda x: x['dialogue_id'])

    # Write outputs
    with open('barem_results_summary_gemini_pro.json', 'w', encoding='utf-8') as f:
        json.dump(all_summary, f, indent=2, ensure_ascii=False)

    with open('barem_results_full_gemini_pro.json', 'w', encoding='utf-8') as f:
        json.dump(all_full_results, f, indent=2, ensure_ascii=False)

    print("Processing complete. Outputs written to barem_results_summary.json and barem_results_full.json")

if __name__ == "__main__":
    main()
