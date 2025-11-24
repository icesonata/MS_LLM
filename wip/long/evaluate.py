import os
import json
import re
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from utils import load_dataset

# Configuration
DATASET_PATH = "/Users/icesonata/schools/llm/MS_LLM/dataset/selected_dialogues.json"
RESULTS_DIR = "/Users/icesonata/schools/llm/MS_LLM/wip/long2/results"

def extract_json(text):
    # Try to find JSON block
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    return None

def get_overall_score(response_text):
    data = extract_json(response_text)
    if data:
        # Check for OverallExperience
        if "OverallExperience" in data:
            val = data["OverallExperience"]
            if isinstance(val, dict):
                return val.get("score")
            return val
        # Check for referee_final in Multi agent debate
        if "referee_final" in data and "OverallExperience" in data["referee_final"]:
            return data["referee_final"]["OverallExperience"]
            
    # Fallback: try to find "OverallExperience": <number> pattern
    match = re.search(r'"OverallExperience":\s*\{?\s*"score":\s*(\d+)', response_text)
    if match:
        return float(match.group(1))
    
    match = re.search(r'"OverallExperience":\s*(\d+)', response_text)
    if match:
        return float(match.group(1))
        
    return None

def main():
    # Load ground truth
    print("Loading dataset...")
    dialogues = load_dataset(DATASET_PATH)
    ground_truth = {}
    for d in dialogues:
        d_id = d['dialogue_id']
        # Use average_score_100 as ground truth
        if 'average_score_100' in d:
            ground_truth[d_id] = d['average_score_100']
        else:
            # Fallback if average_score_100 is missing, maybe calculate from overall_scores?
            # But based on grep, it seems present.
            pass

    print(f"Loaded ground truth for {len(ground_truth)} dialogues.")

    # Evaluate each technique
    techniques = [d for d in os.listdir(RESULTS_DIR) if os.path.isdir(os.path.join(RESULTS_DIR, d))]
    
    results_summary = []

    for technique in techniques:
        tech_dir = os.path.join(RESULTS_DIR, technique)
        files = [f for f in os.listdir(tech_dir) if f.endswith(".txt")]
        
        y_true = []
        y_pred = []
        
        for f in files:
            dialogue_id = int(f.split(".")[0])
            
            if dialogue_id not in ground_truth:
                continue
                
            with open(os.path.join(tech_dir, f), 'r', encoding='utf-8') as file:
                content = file.read()
                
            # Split to get RESPONSE part
            parts = content.split("RESPONSE:")
            if len(parts) < 2:
                continue
            
            response_text = parts[-1]
            score = get_overall_score(response_text)
            
            if score is not None:
                y_true.append(ground_truth[dialogue_id])
                y_pred.append(score)
        
        if not y_true:
            print(f"No valid predictions for {technique}")
            continue
            
        y_true = np.array(y_true)
        y_pred = np.array(y_pred)
        
        mae = mean_absolute_error(y_true, y_pred)
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_true, y_pred)
        
        results_summary.append({
            "Technique": technique,
            "MAE": mae,
            "MSE": mse,
            "RMSE": rmse,
            "R2": r2,
            "Count": len(y_true)
        })

    # Print summary
    print("\n" + "="*80)
    print(f"{'Technique':<25} | {'MAE':<10} | {'MSE':<10} | {'RMSE':<10} | {'R2':<10} | {'Count':<5}")
    print("-" * 80)
    for res in results_summary:
        print(f"{res['Technique']:<25} | {res['MAE']:<10.4f} | {res['MSE']:<10.4f} | {res['RMSE']:<10.4f} | {res['R2']:<10.4f} | {res['Count']:<5}")
    print("="*80)

if __name__ == "__main__":
    main()
