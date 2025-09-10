"""
Main script to run CSAT evaluation experiments
"""

import argparse
import os
import time
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass
from tqdm import tqdm

from models.implementations_v2 import ChatGPTModel, GeminiModel, QwenModel, MistralModel
from pipeline_v2 import DatasetExperiment
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    models: List[str]; datasets: List[str]; sample_size: int
    iterations: int; output_dir: str; plot: bool; verbose: bool
    instruction_cn: str = "请根据客户服务对话评估客户满意度。考虑问题解决情况、服务态度和整体体验。"
    instruction_en: str = "Evaluate customer satisfaction based on the support dialogue. Consider issue resolution, service quality, and overall experience."
    rules: str = ""


def get_models(selected: List[str]) -> List:
    """Get available models based on selection"""
    model_configs = {
        'chatgpt': (ChatGPTModel, "ChatGPT", {'api_key': os.getenv('OPENAI_API_KEY')}),
        'gemini': (GeminiModel, "Gemini", {'api_key': os.getenv('GEMINI_API_KEY')}),
        'qwen': (QwenModel, "Qwen", {'api_key': os.getenv('QWEN_API_KEY')}),
        'mistral': (MistralModel, "Mistral", {'api_key': os.getenv('MISTRAL_API_KEY')})
    }
    
    # Add default config
    for name, (cls, model_name, config) in model_configs.items():
        config.update({'temperature': 0.3, 'max_tokens': 1500})
        if name == 'chatgpt': config['model_version'] = 'gpt-4o'
        elif name == 'gemini': config['model_version'] = 'gemini-2.0-flash'
        elif name == 'qwen': config['model_version'] = 'qwen3-8b'
        elif name == 'mistral': config['model_version'] = 'mistral-small-latest'
    
    models = []
    for name, (cls, model_name, config) in model_configs.items():
        if ('all' in selected or name in selected) and config.get('api_key'):
            models.append(cls(model_name, config))
    
    if not models:
        print(f"No models available. Set API keys: OPENAI_API_KEY, GEMINI_API_KEY, QWEN_API_KEY, MISTRAL_API_KEY")
        exit(1)
    
    return models


def validate_compatibility(models: List, datasets: List[str]) -> None:
    """Warn about Mistral + Chinese dataset compatibility"""
    if any(m.model_name == "Mistral" for m in models) and "JDDC" in datasets:
        print("⚠️  Mistral only supports English. Will skip JDDC dataset.\n")


def run_experiment(config: Config):
    """Run the complete experiment"""
    start_time = time.time()
    
    print(f"Starting: {len(config.models)} models, {len(config.datasets)} datasets, {config.iterations} iterations")
    
    models = get_models(config.models)
    print(f"Models: {[m.model_name for m in models]}")
    validate_compatibility(models, config.datasets)
    
    # Create output directories
    unix_timestamp = int(time.time())
    output_dirs = {}
    for model in models:
        model_dir = f"{unix_timestamp}_{model.model_name}"
        full_path = Path(config.output_dir) / model_dir
        full_path.mkdir(parents=True, exist_ok=True)
        output_dirs[model.model_name] = str(full_path)
    
    experiment = DatasetExperiment(models, config.iterations)
    
    # Calculate total evaluations for progress bar
    from dataloader import load_dataset
    total_evaluations = 0
    for dataset in config.datasets:
        dialogues = load_dataset(dataset)
        sample_size = config.sample_size if config.sample_size and config.sample_size < len(dialogues) else len(dialogues)
        total_evaluations += sample_size * len(models)
    
    print(f"Total evaluations: {total_evaluations}")
    
    # Run experiments with progress tracking
    pbar = tqdm(total=total_evaluations, desc="Processing", unit="eval")
    current_eval = 0
    
    for dataset in config.datasets:
        instruction = config.instruction_cn if dataset == 'JDDC' else config.instruction_en
        dialogues = load_dataset(dataset)
        sample_size = config.sample_size if config.sample_size and config.sample_size < len(dialogues) else len(dialogues)
        
        print(f"\nDataset: {dataset} ({sample_size} samples)")
        
        for model in models:
            print(f"Model: {model.model_name}")
            
            # Skip Mistral for Chinese datasets
            if model.model_name == "Mistral" and dataset == "JDDC":
                print(f"  Skipping {model.model_name} for Chinese dataset")
                for _ in range(sample_size):
                    current_eval += 1
                    pbar.update(1)
                continue
            
            def progress_callback():
                nonlocal current_eval
                current_eval += 1
                pbar.update(1)
                pbar.set_description(f"Processing {model.model_name} on {dataset}")
            
            experiment.run_on_dataset_with_progress(
                dataset, instruction, config.rules, config.sample_size, 
                config.verbose, model, progress_callback
            )
    
    pbar.close()
    
    # Save results and show summary
    print(f"\nSaving results...")
    experiment.save_organized_results(output_dirs, config.plot)
    
    print(f"\nSUMMARY:")
    print(experiment.get_summary().to_string())
    
    total_time = time.time() - start_time
    print(f"\nCompleted in {total_time:.1f}s")
    print(f"\nResults saved to:")
    for model_name, path in output_dirs.items():
        print(f"  {model_name}: {path}/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run CSAT evaluation experiments')
    parser.add_argument('--models', nargs='+', choices=['chatgpt', 'gemini', 'qwen', 'mistral', 'all'], default=['all'])
    parser.add_argument('--datasets', nargs='+', choices=['JDDC', 'MWOZ'], default=['JDDC', 'MWOZ'])
    parser.add_argument('--sample-size', type=int, default=None)
    parser.add_argument('--iterations', type=int, default=5)
    parser.add_argument('--output-dir', type=str, default='results')
    parser.add_argument('--plot', action='store_true')
    parser.add_argument('--verbose', action='store_true')
    
    args = parser.parse_args()
    config = Config(**vars(args))
    run_experiment(config)
