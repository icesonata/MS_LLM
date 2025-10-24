"""
Main script to run CSAT evaluation experiments - Simplified for 7-criteria system with 1-5 scale comparison
"""

import argparse
import os
import time
from pathlib import Path
from typing import List
from dataclasses import dataclass
from tqdm import tqdm

from models.implementations import ChatGPTModel, GeminiModel, QwenModel, MistralModel
from pipeline import DatasetExperiment
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    models: List[str]
    datasets: List[str]
    sample_size: int
    iterations: int
    output_dir: str
    plot: bool
    verbose: bool


def get_models(selected: List[str]) -> List:
    """Initialize and return available models"""
    model_configs = {
        'chatgpt': (ChatGPTModel, "ChatGPT", {'api_key': os.getenv('OPENAI_API_KEY'), 'model_version': 'gpt-4o'}),
        'gemini': (GeminiModel, "Gemini", {'api_key': os.getenv('GEMINI_API_KEY'), 'model_version': 'gemini-2.0-flash'}),
        'qwen': (QwenModel, "Qwen", {'api_key': os.getenv('QWEN_API_KEY'), 'model_version': 'qwen3-30b-a3b-instruct-2507'}),
        'mistral': (MistralModel, "Mistral", {'api_key': os.getenv('MISTRAL_API_KEY'), 'model_version': 'mistral-small-latest'})
    }
    
    # Add default config
    for name, (cls, model_name, config) in model_configs.items():
        config.update({'temperature': 0.3, 'max_tokens': 2000})
    
    models = []
    failed_models = []
    
    for name, (cls, model_name, config) in model_configs.items():
        if 'all' in selected or name in selected:
            try:
                if not config.get('api_key'):
                    failed_models.append(f"{model_name}: Missing API key")
                    continue
                
                model = cls(model_name, config)
                models.append(model)
                print(f"✓ {model_name} initialized")
                
            except Exception as e:
                failed_models.append(f"{model_name}: {str(e)}")
                print(f"✗ {model_name} failed: {e}")
    
    if failed_models:
        print(f"\nFailed models:")
        for failure in failed_models:
            print(f"  - {failure}")
        print(f"\nRequired environment variables:")
        print(f"  OPENAI_API_KEY, GEMINI_API_KEY, QWEN_API_KEY, MISTRAL_API_KEY")
    
    if not models:
        raise RuntimeError("No models initialized. Check API keys.")
    
    return models


def get_dataset_info():
    """Dataset information"""
    return {
        'JDDC': 'Chinese E-commerce Customer Service',
        'MWOZ': 'English Multi-domain Task-oriented',
        'CCPE': 'English Movie Preference Conversations'
    }


def create_output_directory_name(timestamp: int, model_name: str, model_version: str, 
                                datasets: List[str], sample_size: int, iterations: int) -> str:
    """Create descriptive directory name"""
    # Clean model version (remove special characters)
    clean_version = model_version.replace('-', '').replace('.', '')
    
    # Join datasets with underscore
    datasets_str = '_'.join(datasets)
    
    # Sample size string
    sample_str = f"{sample_size}s" if sample_size else "all"
    
    # Create directory name
    dir_name = f"{timestamp}_{model_name}_{clean_version}_{datasets_str}_{sample_str}_{iterations}i"
    
    return dir_name


def run_experiment(config: Config):
    """Run the complete experiment"""
    start_time = time.time()
    
    print("=" * 60)
    print("CSAT EVALUATION EXPERIMENT")
    print("7-criteria system with 1-5 scale comparison")
    print("=" * 60)
    
    # Show configuration
    print(f"Models: {config.models}")
    print(f"Datasets: {config.datasets}")
    print(f"Sample size: {config.sample_size or 'All'}")
    print(f"Iterations: {config.iterations}")
    print(f"Output: {config.output_dir}")
    
    # Dataset info
    dataset_info = get_dataset_info()
    print(f"\nDatasets:")
    for dataset in config.datasets:
        print(f"  {dataset}: {dataset_info.get(dataset, 'Unknown')}")
    
    # Initialize models
    print(f"\nInitializing models...")
    models = get_models(config.models)
    
    # Skip Mistral for Chinese datasets
    if any(m.model_name == "Mistral" for m in models) and "JDDC" in config.datasets:
        print("⚠️  Mistral will skip JDDC (Chinese not supported)")
    
    # Create output directories with descriptive names
    timestamp = int(time.time())
    output_dirs = {}
    
    for model in models:
        # Get model version from config
        model_version = model.config.get('model_version', 'unknown')
        
        dir_name = create_output_directory_name(
            timestamp=timestamp,
            model_name=model.model_name,
            model_version=model_version,
            datasets=config.datasets,
            sample_size=config.sample_size,
            iterations=config.iterations
        )
        
        output_dirs[model.model_name] = str(Path(config.output_dir) / dir_name)
        Path(output_dirs[model.model_name]).mkdir(parents=True, exist_ok=True)
    
    # Initialize experiment
    experiment = DatasetExperiment(models, config.iterations)
    
    # Calculate total work
    from dataloader import load_dataset
    total_work = 0
    dataset_sizes = {}
    
    for dataset in config.datasets[:]:  # Copy to allow modification
        try:
            dialogues = load_dataset(dataset)
            size = min(config.sample_size, len(dialogues)) if config.sample_size else len(dialogues)
            dataset_sizes[dataset] = size
            
            # Count work per model (skip Mistral for JDDC)
            model_count = len(models)
            if dataset == "JDDC":
                model_count -= sum(1 for m in models if m.model_name == "Mistral")
            
            total_work += size * model_count
            
        except FileNotFoundError:
            print(f"⚠️  Dataset {dataset} not found, skipping...")
            config.datasets.remove(dataset)
    
    print(f"\nDataset sizes:")
    for dataset, size in dataset_sizes.items():
        print(f"  {dataset}: {size} samples")
    print(f"Total evaluations: {total_work}")
    
    # Run experiments
    print(f"\nRunning experiments...")
    pbar = tqdm(total=total_work, desc="Processing", unit="eval")
    
    for dataset in config.datasets:
        print(f"\n📊 Dataset: {dataset}")
        
        for model in models:
            # Skip Mistral for Chinese datasets
            if model.model_name == "Mistral" and dataset == "JDDC":
                print(f"  ⏭️  Skipping {model.model_name} (Chinese not supported)")
                continue
            
            print(f"  🤖 {model.model_name}: ", end="", flush=True)
            
            def progress_callback():
                pbar.update(1)
                pbar.set_description(f"{model.model_name} on {dataset}")
            
            try:
                experiment.run_on_dataset_with_progress(
                    dataset, 
                    "Evaluate dialogue satisfaction", 
                    "", 
                    config.sample_size, 
                    config.verbose, 
                    model, 
                    progress_callback
                )
                print("✅ Done")
                
            except Exception as e:
                print(f"❌ Failed: {e}")
                # Skip remaining samples for this model-dataset combination
                remaining = dataset_sizes[dataset]
                for _ in range(remaining):
                    pbar.update(1)
    
    pbar.close()
    
    # Save results
    print(f"\n💾 Saving results...")
    experiment.save_organized_results(output_dirs, config.plot)
    
    # Show summary
    print(f"\n📈 RESULTS SUMMARY")
    print("=" * 80)
    
    summary_df = experiment.get_summary()
    if not summary_df.empty:
        # Show key metrics including MSE
        key_columns = ['Model', 'Dataset', 'MAE', 'MSE', 'RMSE', 'R²', 'Avg_Pred_1_5', 'Avg_GT_1_5']
        display_df = summary_df[key_columns].round(3)
        
        print(display_df.to_string(index=False))
        
        # Best performing model per dataset
        print(f"\n🏆 Best Performance (lowest MAE):")
        for dataset in config.datasets:
            dataset_results = summary_df[summary_df['Dataset'] == dataset]
            if not dataset_results.empty:
                best_model = dataset_results.loc[dataset_results['MAE'].idxmin()]
                print(f"  {dataset}: {best_model['Model']} (MAE: {best_model['MAE']:.3f})")
    else:
        print("No results to display.")
    
    # Execution summary
    total_time = time.time() - start_time
    print(f"\n⏱️  Completed in {total_time:.1f}s")
    
    print(f"\n📁 Results saved to:")
    for model_name, path in output_dirs.items():
        print(f"  {model_name}: {path}")
    
    print(f"\n📋 Files generated per model:")
    print(f"  - summary.csv (metrics overview)")
    if config.datasets:
        print(f"  - {config.datasets[0]}_detailed.txt (detailed report)")
        print(f"  - {config.datasets[0]}_results.csv (per-sample results)")
        print(f"  - {config.datasets[0]}_raw_outputs.json (model responses)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='CSAT Evaluation with 7-criteria system (1-5 scale comparison)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_v2.py --models chatgpt --datasets CCPE --sample-size 10
  python run_v2.py --models all --datasets CCPE MWOZ --iterations 3
  python run_v2.py --models gemini qwen --datasets all --plot
        """
    )
    
    parser.add_argument('--models', nargs='+', 
                       choices=['chatgpt', 'gemini', 'qwen', 'mistral', 'all'], 
                       default=['all'], 
                       help='Models to evaluate (default: all)')
    
    parser.add_argument('--datasets', nargs='+', 
                       choices=['JDDC', 'MWOZ', 'CCPE', 'all'], 
                       default=['CCPE'], 
                       help='Datasets to evaluate (default: CCPE)')
    
    parser.add_argument('--sample-size', type=int, default=None, 
                       help='Limit samples per dataset (default: all)')
    
    parser.add_argument('--iterations', type=int, default=5, 
                       help='Evaluation iterations per dialogue (default: 5)')
    
    parser.add_argument('--output-dir', type=str, default='results', 
                       help='Output directory (default: results)')
    
    parser.add_argument('--plot', action='store_true', 
                       help='Generate plots (requires matplotlib)')
    
    parser.add_argument('--verbose', action='store_true', 
                       help='Verbose output')
    
    args = parser.parse_args()
    
    # Handle 'all' options
    if 'all' in args.datasets:
        args.datasets = ['JDDC', 'MWOZ', 'CCPE']
    
    config = Config(**vars(args))
    
    try:
        run_experiment(config)
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Experiment interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Experiment failed: {e}")
        raise
