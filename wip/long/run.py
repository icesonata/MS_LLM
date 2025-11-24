import os
import json
import re
import numpy as np
from tqdm import tqdm
from dotenv import load_dotenv
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils import QwenModel, load_dataset, format_dialogue, load_prompt
import argparse

# Load environment variables
load_dotenv()

# Configuration
DATASET_PATH = "/Users/icesonata/schools/llm/MS_LLM/dataset/selected_dialogues.json"
PROMPTS_DIR = "/Users/icesonata/schools/llm/MS_LLM/prompts"
OUTPUT_DIR = "/Users/icesonata/schools/llm/MS_LLM/wip/long2/results"

TECHNIQUES = {
    "Baseline": "baseline_origin.txt",
    "CoT": "cot.txt",
    "Barem": "barem.txt",
    "Self-consistency": "self_consistency.txt",
    "Multi agent debate": "multiagent_debate.txt",
    "Auto CoT": "auto_cot.txt"
}

class TfidfEmbedder:
    def __init__(self):
        self.vec = TfidfVectorizer(max_features=2048)
        self.fit = False
        
    def encode(self, texts):
        if not self.fit:
            m = self.vec.fit_transform(texts)
            self.fit = True
        else:
            m = self.vec.transform(texts)
        return m.toarray().astype("float32")

class ExampleRetriever:
    def __init__(self, examples):
        self.examples = examples
        self.embedder = TfidfEmbedder()
        self.example_texts = [ex['text'] for ex in examples]
        self.example_embeddings = self.embedder.encode(self.example_texts)
        
    def retrieve(self, query_text, k=1):
        query_embedding = self.embedder.encode([query_text])
        scores = cosine_similarity(query_embedding, self.example_embeddings)[0]
        top_k_indices = np.argsort(scores)[::-1][:k]
        return [self.examples[i] for i in top_k_indices]

def parse_barem_examples(barem_path):
    with open(barem_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    examples = []
    # Regex to find examples in barem.txt
    # Pattern: (Example X — dialogue_id Y)... text ... Expected ... {json}
    
    # Split by example headers
    parts = re.split(r'\(Example \d+ — dialogue_id \d+\)', content)
    
    # Skip the first part (intro)
    for i in range(1, len(parts)):
        part = parts[i]
        
        # Extract dialogue text (up to "Expected")
        dialogue_match = re.search(r'(.*?)Expected', part, re.DOTALL)
        if not dialogue_match:
            continue
        dialogue_text = dialogue_match.group(1).strip()
        
        # Extract JSON
        json_match = re.search(r'(\{.*\})', part, re.DOTALL)
        if not json_match:
            continue
        json_text = json_match.group(1).strip()
        
        # Clean up JSON text (remove trailing text if any)
        # Find the last closing brace
        last_brace = json_text.rfind('}')
        if last_brace != -1:
            json_text = json_text[:last_brace+1]
            
        try:
            evaluation = json.loads(json_text)
            
            # Map keys to Auto CoT schema
            mapped_eval = {}
            key_map = {
                "TaskSuccess": "TaskSuccess",
                "Helpfulness": "HelpfulnessRelevance",
                "Accuracy": "FaithfulnessAccuracy",
                "Understanding": "Understanding",
                "Empathy": "Empathy",
                "Fluency": "FluencyCoherence",
                "OverallExperience": "OverallExperience"
            }
            
            for k, v in evaluation.items():
                new_key = key_map.get(k, k)
                mapped_eval[new_key] = v
                
            examples.append({
                "text": dialogue_text,
                "evaluation": mapped_eval
            })
        except json.JSONDecodeError:
            print(f"Warning: Could not parse JSON for example {i}")
            continue
            
    return examples

def extract_json(text):
    # Try to find JSON block
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    return None

def extract_score(text, technique):
    # Check for error response first
    if "Error:" in text and "{" in text and "}" in text:
         # It might be an API error JSON
         pass

    if technique == "CoT":
        # Look for <score> tags
        match = re.search(r'<score>\s*(\d+(?:\.\d+)?)\s*</score>', text)
        if match:
            return float(match.group(1))
            
        # Fallback: Look for "Overall score: X" pattern from few-shot examples
        match = re.search(r'Overall score:\s*(\d+(?:\.\d+)?)', text, re.IGNORECASE)
        if match:
            return float(match.group(1))
    
    # Try to parse as JSON for other techniques
    data = extract_json(text)
    if data:
        # Multi agent debate
        if technique == "Multi agent debate":
            if "referee_final" in data and "OverallExperience" in data["referee_final"]:
                val = data["referee_final"]["OverallExperience"]
                if isinstance(val, dict):
                    return float(val.get("score", 0))
                return float(val)
        
        # Others
        if "OverallExperience" in data:
            val = data["OverallExperience"]
            if isinstance(val, dict):
                return float(val.get("score", 0))
            return float(val)

    # Fallback regex for OverallExperience
    match = re.search(r'"OverallExperience":\s*\{?\s*"score":\s*(\d+)', text)
    if match:
        return float(match.group(1))
    
    match = re.search(r'"OverallExperience":\s*(\d+)', text)
    if match:
        return float(match.group(1))

    return None

def calculate_metrics(y_true, y_pred):
    if not y_true or not y_pred:
        return None
    
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    
    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_true, y_pred)
    
    return {
        "MAE": mae,
        "MSE": mse,
        "RMSE": rmse,
        "R2": r2,
        "Count": len(y_true)
    }

def construct_prompt(technique, template, dialogue_text, retriever=None):
    if technique in ["Baseline", "Barem", "Self-consistency"]:
        return template.replace("{{dialogue_transcript}}", dialogue_text)
    
    elif technique == "CoT":
        # Append target dialogue
        return template + f"\n\n- Target Dialogue:\n{dialogue_text}\n\nPlease evaluate this dialogue and provide the score inside <score> tags."
    
    elif technique == "Multi agent debate":
        # Append target dialogue
        return template + f"\n\n=== TARGET DIALOGUE ===\n{dialogue_text}\n\nExpected output:"
    
    elif technique == "Auto CoT":
        # Dynamic retrieval
        example_text = ""
        if retriever:
            retrieved_examples = retriever.retrieve(dialogue_text, k=1)
            if retrieved_examples:
                ex = retrieved_examples[0]
                example_text = f"Dialogue:\n{ex['text']}\n\nEvaluation JSON:\n{json.dumps(ex['evaluation'], indent=2)}"
        
        # Replace the example section in template
        # The template has "--- Few-Shot Example ---" followed by a static example
        marker = "--- Few-Shot Example ---"
        if marker in template:
            parts = template.split(marker)
            base_prompt = parts[0] + marker + "\n"
            
            if example_text:
                # Use retrieved example
                full_prompt = base_prompt + example_text + f"\n\n=== Target Dialogue To Evaluate ===\n{dialogue_text}"
                return full_prompt
            else:
                # Fallback to static example if retrieval failed (shouldn't happen if pool exists)
                return template + f"\n\n=== Target Dialogue To Evaluate ===\n{dialogue_text}"
        else:
             return template + f"\n\n=== Target Dialogue To Evaluate ===\n{dialogue_text}"
    
    return template

def main():
    parser = argparse.ArgumentParser(description="Run LLM evaluation")
    parser.add_argument("--runs", type=int, default=1, help="Number of times to run the evaluation")
    args = parser.parse_args()
    n_runs = args.runs

    # Load dataset
    dialogues = load_dataset(DATASET_PATH)
    
    # Filter out few-shot examples used in prompts
    few_shot_ids = [335, 25, 26]
    test_dialogues = [d for d in dialogues if d.get('dialogue_id') not in few_shot_ids]
    
    print(f"Total dialogues: {len(dialogues)}")
    print(f"Test dialogues: {len(test_dialogues)} (Excluded IDs: {few_shot_ids})")
    print(f"Number of runs: {n_runs}")
    
    # Initialize Model
    model = QwenModel()
    print(f"Model initialized: {model.model_version}")
    
    # Create output directory
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Initialize Retriever for Auto CoT
    retriever = None
    barem_path = os.path.join(PROMPTS_DIR, "barem.txt")
    if os.path.exists(barem_path):
        examples = parse_barem_examples(barem_path)
        if examples:
            retriever = ExampleRetriever(examples)
            print(f"Initialized Auto CoT retriever with {len(examples)} examples.")
        else:
            print("Warning: No examples parsed from barem.txt")
    else:
        print("Warning: barem.txt not found for example retrieval")

    # Load ground truth map
    ground_truth_map = {}
    for d in dialogues:
        if 'average_score' in d:
            ground_truth_map[d['dialogue_id']] = d['average_score']
            
    all_run_metrics = {tech: [] for tech in TECHNIQUES}
    
    for run_idx in range(1, n_runs + 1):
        print(f"\n{'='*20} Run {run_idx}/{n_runs} {'='*20}")
        
        # Run evaluation
        for technique, filename in TECHNIQUES.items():
            print(f"\nRunning technique: {technique}")
            
            # Load prompt template
            prompt_path = os.path.join(PROMPTS_DIR, filename)
            try:
                template = load_prompt(prompt_path)
            except FileNotFoundError:
                print(f"Warning: Prompt file {filename} not found. Skipping.")
                continue
                
            if n_runs > 1:
                technique_dir = os.path.join(OUTPUT_DIR, f"run_{run_idx}", technique.replace(" ", "_"))
            else:
                technique_dir = os.path.join(OUTPUT_DIR, technique.replace(" ", "_"))
                
            if not os.path.exists(technique_dir):
                os.makedirs(technique_dir)
                
            for dialogue in tqdm(test_dialogues, desc=f"Evaluating {technique}"):
                dialogue_id = dialogue.get('dialogue_id')
                dialogue_text = format_dialogue(dialogue.get('turns', []))
                
                # Construct prompt
                full_prompt = construct_prompt(technique, template, dialogue_text, retriever if technique == "Auto CoT" else None)
                
                # Generate response with retry
                max_retries = 3
                response = ""
                for attempt in range(max_retries):
                    response = model.generate(full_prompt)
                    
                    # Check if we can extract a score
                    score = extract_score(response, technique)
                    if score is not None:
                        break
                    
                    # If we are here, extraction failed
                    if attempt < max_retries - 1:
                        # Optional: Add a small delay or log
                        pass
                
                # Save result
                output_file = os.path.join(technique_dir, f"{dialogue_id}.txt")
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(f"Dialogue ID: {dialogue_id}\n")
                    f.write(f"Technique: {technique}\n")
                    f.write("-" * 50 + "\n")
                    f.write("PROMPT:\n")
                    f.write(full_prompt)
                    f.write("\n" + "-" * 50 + "\n")
                    f.write("RESPONSE:\n")
                    f.write(response)

            # Evaluation Phase for this technique
            print(f"\nEvaluating results for {technique}...")
            y_true = []
            y_pred = []
            parsed_outputs = []
            
            files = [f for f in os.listdir(technique_dir) if f.endswith(".txt")]
            for f in files:
                try:
                    dialogue_id = int(f.split(".")[0])
                except ValueError:
                    continue
                
                # Ignore few-shot samples
                if dialogue_id in few_shot_ids:
                    continue
                    
                if dialogue_id not in ground_truth_map:
                    continue
                    
                with open(os.path.join(technique_dir, f), 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                parts = content.split("RESPONSE:")
                if len(parts) < 2:
                    continue
                    
                response_text = parts[-1]
                score = extract_score(response_text, technique)
                json_data = extract_json(response_text)
                
                # Convert score to 1-5 scale to match long1 logic
                score_5 = score / 20.0 if score is not None and score != 0 else None
                
                parsed_outputs.append({
                    "dialogue_id": dialogue_id,
                    "extracted_score": score,
                    "extracted_score_5": score_5,
                    "ground_truth": ground_truth_map[dialogue_id],
                    "model_output": json_data
                })
                
                if score_5 is not None:
                    y_true.append(ground_truth_map[dialogue_id])
                    y_pred.append(score_5)
            
            # Save parsed outputs
            if n_runs > 1:
                eval_file = os.path.join(OUTPUT_DIR, f"run_{run_idx}", f"{technique.replace(' ', '_')}_eval.json")
            else:
                eval_file = os.path.join(OUTPUT_DIR, f"{technique.replace(' ', '_')}_eval.json")
                
            with open(eval_file, "w", encoding="utf-8") as f:
                json.dump(parsed_outputs, f, indent=4)
            
            metrics = calculate_metrics(y_true, y_pred)
            if metrics:
                all_run_metrics[technique].append(metrics)
                print(f"Technique: {technique}")
                print(f"Count: {metrics['Count']}")
                print(f"MAE: {metrics['MAE']:.4f}")
                print(f"MSE: {metrics['MSE']:.4f}")
                print(f"RMSE: {metrics['RMSE']:.4f}")
                print(f"R2: {metrics['R2']:.4f}")
            else:
                print(f"Technique: {technique} - No valid predictions found.")

    # Calculate and save aggregated summary
    final_summary = []
    print(f"\n{'='*20} Aggregated Results ({n_runs} runs) {'='*20}")
    
    for technique, metrics_list in all_run_metrics.items():
        if not metrics_list:
            continue
            
        agg_metrics = {"Technique": technique, "Runs": len(metrics_list)}
        
        # Calculate mean and std for each metric
        for key in ["MAE", "MSE", "RMSE", "R2"]:
            values = [m[key] for m in metrics_list]
            agg_metrics[f"{key}_mean"] = float(np.mean(values))
            agg_metrics[f"{key}_std"] = float(np.std(values))
        
        # Also average the count
        counts = [m["Count"] for m in metrics_list]
        agg_metrics["Count_mean"] = float(np.mean(counts))
        
        final_summary.append(agg_metrics)
        
        print(f"\nTechnique: {technique}")
        print(f"MAE: {agg_metrics['MAE_mean']:.4f} ± {agg_metrics['MAE_std']:.4f}")
        print(f"MSE: {agg_metrics['MSE_mean']:.4f} ± {agg_metrics['MSE_std']:.4f}")
        print(f"RMSE: {agg_metrics['RMSE_mean']:.4f} ± {agg_metrics['RMSE_std']:.4f}")
        print(f"R2: {agg_metrics['R2_mean']:.4f} ± {agg_metrics['R2_std']:.4f}")

    # Save summary
    summary_file = "evaluation_summary_aggregated.json" if n_runs > 1 else "evaluation_summary.json"
    with open(os.path.join(OUTPUT_DIR, summary_file), "w", encoding="utf-8") as f:
        json.dump(final_summary, f, indent=4)

if __name__ == "__main__":
    main()
