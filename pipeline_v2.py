"""
Simplified pipeline for CSAT evaluation with multiple iterations
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
import numpy as np
import pandas as pd
from pathlib import Path
import json
from datetime import datetime

from dataloader import load_dataset, Language
from models.base import BaseCSATModel, CSATInput, CSATOutput


@dataclass
class CSATResult:
    """Result after multiple iterations"""
    average_score: float
    all_scores: List[int]
    variance: float
    final_explanation: str
    golden_synthesis_samples: List[str]
    ground_truth: Optional[float] = None
    mae: Optional[float] = None


class CSATPipeline:
    """Main pipeline for CSAT evaluation"""
    
    def __init__(self, model: BaseCSATModel, num_iterations: int = 5):
        self.model = model
        self.num_iterations = num_iterations
    
    def evaluate_dialogue(self, dialogue, instruction_prompt: str, rule_based_prompt: str = "") -> CSATResult:
        """Evaluate a single dialogue with multiple iterations"""
        csat_input = CSATInput(
            instruction_prompt=instruction_prompt,
            rule_based_prompt=rule_based_prompt,
            dialogue=dialogue.to_text(),
            language=dialogue.language
        )
        
        outputs, scores = [], []
        
        for _ in range(self.num_iterations):
            try:
                output = self.model.predict(csat_input)
                outputs.append(output)
                scores.append(output.score)
            except Exception as e:
                print(f"Error in iteration: {e}")
                scores.append(3)
        
        # Calculate statistics
        average_score = np.mean(scores)
        variance = np.var(scores)
        
        # Aggregate golden synthesis samples
        all_golden_samples = []
        for output in outputs:
            if output and hasattr(output, 'golden_synthesis'):
                all_golden_samples.extend(output.golden_synthesis)
        
        # Select best explanation
        if outputs:
            best_idx = np.argmin(np.abs(np.array(scores) - average_score))
            best_explanation = outputs[best_idx].explanation if best_idx < len(outputs) else "No explanation"
        else:
            best_explanation = "No explanation"
        
        # Calculate MAE if ground truth available
        ground_truth = dialogue.average_satisfaction
        mae = abs(average_score - ground_truth) if ground_truth else None
        
        return CSATResult(
            average_score=float(average_score),
            all_scores=scores,
            variance=float(variance),
            final_explanation=best_explanation,
            golden_synthesis_samples=list(set(all_golden_samples))[:5],
            ground_truth=ground_truth,
            mae=mae
        )


class DatasetExperiment:
    """Run experiments on datasets"""
    
    def __init__(self, models: List[BaseCSATModel], num_iterations: int = 5):
        self.models = models
        self.num_iterations = num_iterations
        self.results = {}
    
    def run_on_dataset_with_progress(self, dataset_name: str, instruction_prompt: str, 
                                   rule_based_prompt: str = "", sample_size: Optional[int] = None, 
                                   verbose: bool = True, model: BaseCSATModel = None, 
                                   progress_callback=None):
        """Run experiment on a dataset with progress tracking"""
        dialogues = load_dataset(dataset_name)
        if sample_size and sample_size < len(dialogues):
            import random
            random.seed(42)
            dialogues = random.sample(dialogues, sample_size)
        
        models_to_run = [model] if model else self.models
        
        for current_model in models_to_run:
            pipeline = CSATPipeline(current_model, self.num_iterations)
            model_results = []
            
            for dialogue in dialogues:
                result = pipeline.evaluate_dialogue(dialogue, instruction_prompt, rule_based_prompt)
                model_results.append(result)
                
                if progress_callback:
                    progress_callback()
            
            key = f"{current_model.model_name}_{dataset_name}"
            self.results[key] = {
                'model_name': current_model.model_name,
                'dataset': dataset_name,
                'results': model_results,
                'metrics': self._calculate_metrics(model_results)
            }
    
    def _calculate_metrics(self, results: List[CSATResult]) -> Dict[str, float]:
        """Calculate evaluation metrics"""
        predictions = [r.average_score for r in results]
        ground_truths = [r.ground_truth for r in results if r.ground_truth is not None]
        
        metrics = {
            'avg_predicted_score': float(np.mean(predictions)),
            'avg_variance': float(np.mean([r.variance for r in results]))
        }
        
        if ground_truths:
            predictions = np.array(predictions[:len(ground_truths)])
            ground_truths = np.array(ground_truths)
            
            metrics.update({
                'mae': float(np.mean(np.abs(predictions - ground_truths))),
                'rmse': float(np.sqrt(np.mean((predictions - ground_truths) ** 2))),
                'correlation': float(np.corrcoef(predictions, ground_truths)[0, 1]) if len(predictions) > 1 else 0,
                'accuracy_1': float(np.mean(np.abs(predictions - ground_truths) <= 1))
            })
        
        return metrics
    
    def get_summary(self) -> pd.DataFrame:
        """Get summary of all experiments"""
        summary_data = []
        for key, result in self.results.items():
            metrics = result['metrics']
            summary_data.append({
                'Model': result['model_name'],
                'Dataset': result['dataset'],
                'MAE': metrics.get('mae', np.nan),
                'RMSE': metrics.get('rmse', np.nan),
                'Correlation': metrics.get('correlation', np.nan),
                'Accuracy (±1)': metrics.get('accuracy_1', np.nan),
                'Avg Variance': metrics.get('avg_variance', np.nan)
            })
        return pd.DataFrame(summary_data)
    
    def save_organized_results(self, output_dirs: Dict[str, str], plot: bool = False):
        """Save results organized by model"""
        for model_name, output_dir in output_dirs.items():
            output_path = Path(output_dir)
            model_results = {k: v for k, v in self.results.items() if v['model_name'] == model_name}
            
            if not model_results:
                continue
            
            # Save summary
            summary_data = []
            for key, result in model_results.items():
                metrics = result['metrics']
                summary_data.append({
                    'Dataset': result['dataset'],
                    'MAE': metrics.get('mae', 0),
                    'RMSE': metrics.get('rmse', 0),
                    'Correlation': metrics.get('correlation', 0),
                    'Accuracy (±1)': metrics.get('accuracy_1', 0),
                    'Avg Variance': metrics.get('avg_variance', 0)
                })
            
            if summary_data:
                pd.DataFrame(summary_data).to_csv(output_path / "summary.csv", index=False)
            
            # Save detailed results
            for key, result in model_results.items():
                dataset_name = result['dataset']
                
                with open(output_path / f"{dataset_name}_detailed.txt", 'w', encoding='utf-8') as f:
                    f.write(f"Model: {model_name} | Dataset: {dataset_name}\n")
                    f.write("="*60 + "\n\n")
                    
                    metrics = result['metrics']
                    f.write("Overall Performance:\n")
                    f.write(f"  Average Score: {metrics.get('avg_predicted_score', 0):.2f}\n")
                    f.write(f"  MAE: {metrics.get('mae', 0):.3f}\n")
                    f.write(f"  RMSE: {metrics.get('rmse', 0):.3f}\n")
                    f.write(f"  Correlation: {metrics.get('correlation', 0):.3f}\n")
                    f.write(f"  Accuracy (±1): {metrics.get('accuracy_1', 0):.3f}\n")
                    f.write(f"  Variance: {metrics.get('avg_variance', 0):.3f}\n\n")
                    
                    f.write(f"Sample Results ({len(result['results'])} total):\n")
                    f.write("-"*50 + "\n")
                    
                    for i, r in enumerate(result['results']):
                        f.write(f"\nSample {i+1}:\n")
                        f.write(f"  Average Score: {r.average_score:.2f}\n")
                        f.write(f"  Scores per iteration: {r.all_scores}\n")
                        f.write(f"  Ground Truth: {r.ground_truth:.2f}\n" if r.ground_truth else "  Ground Truth: N/A\n")
                        f.write(f"  Variance: {r.variance:.3f}\n")
                        f.write(f"  MAE: {r.mae:.3f}\n" if r.mae else "  MAE: N/A\n")
                        
                        if r.golden_synthesis_samples:
                            f.write(f"  Golden Synthesis References:\n")
                            for j, sample in enumerate(r.golden_synthesis_samples[:3], 1):
                                f.write(f"    {j}. {sample}\n")
                        
                        f.write(f"  Explanation: {r.final_explanation}\n")
                        f.write("  " + "-"*40 + "\n")
                
                # Save CSV
                csv_data = []
                for r in result['results']:
                    csv_data.append({
                        'predicted_score': r.average_score,
                        'ground_truth': r.ground_truth,
                        'variance': r.variance,
                        'mae': r.mae,
                        'all_scores': str(r.all_scores),
                        'explanation': r.final_explanation[:200]
                    })
                pd.DataFrame(csv_data).to_csv(output_path / f"{dataset_name}_results.csv", index=False)
            
            # Save JSON summary
            json_results = {}
            for key, result in model_results.items():
                json_results[key] = {
                    'model_name': result['model_name'],
                    'dataset': result['dataset'],
                    'metrics': result['metrics'],
                    'num_samples': len(result['results'])
                }
            
            with open(output_path / "experiment_summary.json", 'w', encoding='utf-8') as f:
                json.dump(json_results, f, indent=2, ensure_ascii=False)
            
            if plot:
                CSATAnalyzer.plot_model_results(self, model_name, str(output_path / "analysis_plots.png"))
            
            print(f"Results for {model_name} saved to: {output_path}")


class CSATAnalyzer:
    """Analyze CSAT prediction results"""
    
    @staticmethod
    def plot_model_results(experiment: DatasetExperiment, model_name: str, save_path: str):
        """Create visualization for a specific model"""
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns
            
            model_results = {k: v for k, v in experiment.results.items() if v['model_name'] == model_name}
            
            if not model_results:
                return
            
            all_predictions, all_ground_truths = [], []
            for key, result in model_results.items():
                for r in result['results']:
                    if r.ground_truth is not None:
                        all_predictions.append(r.average_score)
                        all_ground_truths.append(r.ground_truth)
            
            if not all_predictions:
                return
            
            fig, axes = plt.subplots(2, 2, figsize=(12, 10))
            fig.suptitle(f'CSAT Results - {model_name}', fontsize=16)
            
            # Predictions vs Ground Truth
            axes[0,0].scatter(all_ground_truths, all_predictions, alpha=0.6)
            axes[0,0].plot([1, 5], [1, 5], 'r--', label='Perfect prediction')
            axes[0,0].set_xlabel('Ground Truth')
            axes[0,0].set_ylabel('Predicted')
            axes[0,0].set_title('Predictions vs Ground Truth')
            axes[0,0].legend()
            
            # Error distribution
            errors = np.array(all_predictions) - np.array(all_ground_truths)
            axes[0,1].hist(errors, bins=20, alpha=0.7, edgecolor='black')
            axes[0,1].set_xlabel('Prediction Error')
            axes[0,1].set_ylabel('Frequency')
            axes[0,1].set_title('Error Distribution')
            axes[0,1].axvline(x=0, color='r', linestyle='--')
            
            # Dataset comparison
            dataset_metrics = []
            for key, result in model_results.items():
                dataset_metrics.append({
                    'Dataset': result['dataset'],
                    'MAE': result['metrics'].get('mae', 0),
                    'RMSE': result['metrics'].get('rmse', 0)
                })
            
            if dataset_metrics:
                df = pd.DataFrame(dataset_metrics)
                df.set_index('Dataset')[['MAE', 'RMSE']].plot(kind='bar', ax=axes[1,0])
                axes[1,0].set_title('Error Metrics by Dataset')
                axes[1,0].set_ylabel('Error')
            
            # Variance distribution
            variances = [r.variance for result in model_results.values() for r in result['results']]
            axes[1,1].hist(variances, bins=20, alpha=0.7, edgecolor='black')
            axes[1,1].set_xlabel('Prediction Variance')
            axes[1,1].set_ylabel('Frequency')
            axes[1,1].set_title('Variance Distribution')
            
            plt.tight_layout()
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
        except ImportError:
            print("Install matplotlib and seaborn for plotting")
    
    @staticmethod
    def generate_report(experiment: DatasetExperiment) -> str:
        """Generate detailed text report"""
        report = [
            "=" * 80,
            "CSAT EVALUATION EXPERIMENT REPORT",
            "=" * 80,
            f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "SUMMARY STATISTICS",
            "-" * 40,
            experiment.get_summary().to_string(),
            ""
        ]
        
        for key, result in experiment.results.items():
            report.extend([
                f"\n{'='*60}",
                f"Model: {result['model_name']} | Dataset: {result['dataset']}",
                f"{'='*60}",
                "\nMetrics:"
            ])
            
            for metric_name, value in result['metrics'].items():
                if isinstance(value, float):
                    report.append(f"  {metric_name}: {value:.4f}")
            
            report.append("\nSample Predictions (first 3):")
            for i, r in enumerate(result['results'][:3]):
                report.extend([
                    f"\n  Sample {i+1}:",
                    f"    Predicted: {r.average_score:.2f}",
                    f"    Ground Truth: {r.ground_truth:.2f}" if r.ground_truth else "    Ground Truth: N/A",
                    f"    Variance: {r.variance:.3f}",
                    f"    Explanation: {r.final_explanation[:100]}..."
                ])
        
        return "\n".join(report)
