#!/bin/bash

# Quick test (3 samples, 2 iterations)
python3 run_v2.py --models gemini --sample-size 3 --iterations 2

# Test individual models on all datasets
python3 run_v2.py --models gemini --sample-size 10 --iterations 5 --verbose
python3 run_v2.py --models chatgpt --sample-size 10 --iterations 5 --verbose
python3 run_v2.py --models qwen --sample-size 10 --iterations 5 --verbose

# Test individual models on specific datasets
python3 run_v2.py --models gemini --datasets JDDC --sample-size 15 --plot
python3 run_v2.py --models gemini --datasets MWOZ --sample-size 15 --plot
python3 run_v2.py --models chatgpt --datasets JDDC --sample-size 15 --plot
python3 run_v2.py --models chatgpt --datasets MWOZ --sample-size 15 --plot
python3 run_v2.py --models qwen --datasets JDDC --sample-size 15 --plot
python3 run_v2.py --models qwen --datasets MWOZ --sample-size 15 --plot

# Compare all models on all datasets
python3 run_v2.py --models all --datasets JDDC MWOZ --sample-size 20 --iterations 5 --plot --verbose

# Compare all models on specific datasets
python3 run_v2.py --models all --datasets JDDC --sample-size 30 --iterations 5 --plot --verbose
python3 run_v2.py --models all --datasets MWOZ --sample-size 30 --iterations 5 --plot --verbose

# Production runs on all datasets
python3 run_v2.py --models all --datasets JDDC MWOZ --sample-size 50 --iterations 10 --plot
python3 run_v2.py --models gemini chatgpt --datasets JDDC MWOZ --sample-size 100 --iterations 5 --plot

# Production runs on specific datasets
python3 run_v2.py --models all --datasets JDDC --sample-size 100 --iterations 10 --plot
python3 run_v2.py --models all --datasets MWOZ --sample-size 100 --iterations 10 --plot

# Multiple models comparison on specific datasets
python3 run_v2.py --models gemini qwen --datasets JDDC --sample-size 30 --iterations 3 --plot --verbose
python3 run_v2.py --models chatgpt gemini --datasets MWOZ --sample-size 30 --iterations 3 --plot --verbose

# Large scale evaluation
python3 run_v2.py --models all --datasets JDDC MWOZ --sample-size 200 --iterations 10 --plot --verbose
