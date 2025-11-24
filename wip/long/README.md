# Evaluation Scripts

This directory contains scripts to evaluate LLM performance on dialogue datasets using various prompting techniques.

## Prerequisites

1.  **Python**: Ensure you have Python installed.
2.  **Dependencies**: Install the required Python packages.
    ```bash
    pip install openai python-dotenv scikit-learn numpy tqdm
    ```
3.  **Environment Variables**:
    Create a `.env` file in the root of the project (or ensure it exists) and add your Qwen API key:
    ```
    QWEN_API_KEY=your_api_key_here
    ```

## Usage

### Running the Evaluation

To run the evaluation pipeline:

```bash
python run.py
```

This script will:
1.  Load the dataset from `../../dataset/selected_dialogues.json`.
2.  Apply various prompting techniques (Baseline, CoT, Barem, etc.).
3.  Query the Qwen model.
4.  Save the results in the `results/` directory.
5.  Calculate and print metrics (MAE, MSE, RMSE, R2).

**Options:**

*   `--runs <number>`: Specify the number of times to run the evaluation (default is 1).
    ```bash
    python run.py --runs 3
    ```

### Analyzing Results

The `run.py` script automatically calculates and prints metrics. However, you can also run the standalone evaluation script to re-calculate metrics from the saved results:

```bash
python evaluate.py
```

## Directory Structure

*   `run.py`: Main script to execute the evaluation.
*   `evaluate.py`: Script to calculate metrics from saved results.
*   `utils.py`: Utility functions for model interaction and data loading.
*   `results/`: Directory where output JSON files are stored.
