# CSAT Evaluation Pipeline

A comprehensive pipeline for evaluating Customer Satisfaction (CSAT) scores from dialogue data using multiple language models.

## Features

- **Multi-language Support**: Handles both Chinese (JDDC) and English (MWOZ) datasets
- **Multiple Model Support**: GPT-4, Claude, Llama, and mock models for testing
- **Variance Analysis**: Multiple iterations per dialogue to measure prediction stability
- **Comprehensive Metrics**: MAE, RMSE, correlation, accuracy metrics
- **Detailed Reporting**: Generates reports with explanations and golden synthesis samples
- **Visualization**: Creates plots for result analysis

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd MS_LLM


### Advanced Usage

```bash
# Run on specific datasets with custom prompts
python3 run.py \
    --datasets JDDC MWOZ \
    --sample-size 50 \
    --iterations 3 \
    --instruction-cn "评估客户满意度" \
    --instruction-en "Evaluate satisfaction" \
    --rules "Focus on resolution and empathy" \
    --output-dir results \
    --plot \
    --verbose
```

Dry-run
```bash
# Run with Gemini only
python3 run.py \
    --models gemini \
    --datasets JDDC MWOZ \
    --sample-size 1 \
    --iterations 3 \
    --output-dir results_gemini \
    --verbose
```

```bash
python3 run.py \
    --models gemini \
    --datasets JDDC MWOZ \
    --sample-size 1 \
    --iterations 3 \
    --output-dir results_gemini \
    --verbose
```