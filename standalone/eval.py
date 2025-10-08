import pandas as pd
import json
import copy
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
      

def split_data_label(data):
    print(f"Split_data_label for {len(data)} records.")
    preprocess_dialogue_data = copy.deepcopy(data)

    # score each dialogue
    average_scores = []
    average_score_100 = []
    overall_scores = []
    for dialogue in preprocess_dialogue_data:
        average_scores.append({"dialogue_id": dialogue['dialogue_id'], "average_scores": dialogue['average_score']})
        average_score_100.append({"dialogue_id": dialogue['dialogue_id'], "average_score_100": dialogue['average_score_100']})
        overall_scores.append({"dialogue_id": dialogue['dialogue_id'], "overall_scores": dialogue['overall_scores']})

    # Preprocess into data and label (scores)
    
    for dialogue in preprocess_dialogue_data:
        for turn in dialogue['turns']:
            # remove the "scores" field
            if 'scores' in turn:
                del turn['scores']
            if 'intent' in turn:
                del turn['intent']
            
    data_inference = []
    for dialogue in preprocess_dialogue_data:
        dialogue_text = ""
        for turn in dialogue['turns']:
            dialogue_text += turn['speaker'] + ": " + turn['text'] + "\n"
        data_inference.append({"dialogue_id": dialogue['dialogue_id'], "text": dialogue_text})
        
    return data_inference, average_scores, average_score_100, overall_scores

def calculate_all_metrics(y_true, y_pred):
    """
    Calculates MAE, MSE, RMSE, and R-squared and returns them in a dictionary.
    
    Args:
        y_true (list or np.array): True Average Scores (in dataset).
        y_pred (list or np.array): Predicted Average Scores (model generated).
    """
    mae = round(mean_absolute_error(y_true, y_pred), 4)
    mse = round(mean_squared_error(y_true, y_pred), 4)
    rmse = float(round(np.sqrt(mse), 4))
    r2 = round(r2_score(y_true, y_pred), 4)
    
    metrics = {
        'MAE': mae,
        'MSE': mse,
        'RMSE': rmse,
        'R2': r2
    }
    
    return metrics

def main():
    with open("selected_dialogues.json", "r") as f:
        data = json.load(f)

    # data_sample is the data in barem so remove it in data
    data_sample = []
    data_inference = []

    for dialogue in data['dialogues']:
        if (dialogue['dialogue_id'] in {335, 25, 26}):
            data_sample.append(dialogue)
        else:
            data_inference.append(dialogue)
            
    print("Number of sample dialogues:", len(data_sample))
    print("Number of inference dialogues:", len(data_inference))

    data_inference, average_scores, average_score_100, overall_scores = split_data_label(data_inference)

    with open("result.json", "r") as f:
        result = json.load(f)
        
    result_df = pd.DataFrame(result)
    df = pd.DataFrame(average_scores)

    result_df = result_df.join(df, on='dialogue_id', lsuffix='_left', rsuffix='_right')
    result_df = result_df[['dialogue_id', 'average_scores', 'model_score']]
    result_df['model_score_5'] = result_df['model_score'] / 20
    result_df.drop(columns=['model_score'], inplace=True)
    result_df = result_df.dropna()

    metrics_list = []
    metrics = calculate_all_metrics(result_df['average_scores'], result_df['model_score_5'])
    metrics_list.append(metrics)

    all_results = {
        'mean': {
            'MAE': float(np.mean([m['MAE'] for m in metrics_list])),
            'MSE': float(np.mean([m['MSE'] for m in metrics_list])),
            'RMSE': float(np.mean([m['RMSE'] for m in metrics_list])),
            'R2': float(np.mean([m['R2'] for m in metrics_list])),
            },
            'sd' :{
            'MAE': float(np.std([m['MAE'] for m in metrics_list])),
            'MSE': float(np.std([m['MSE'] for m in metrics_list])),
            'RMSE': float(np.std([m['RMSE'] for m in metrics_list])),
            'R2': float(np.std([m['R2'] for m in metrics_list])),
        }
    }
    print(all_results)

if __name__ == "__main__":
    main()