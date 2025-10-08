"""
Simplified pipeline for CSAT evaluation with multiple iterations - Updated for 7-criteria system with 1-5 scale comparison
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
import numpy as np
import pandas as pd
from pathlib import Path
import json
from datetime import datetime

from dataloader import load_dataset, Language
from models.base import BaseCSATModel, CSATInput, CSATOutput, CriteriaScore


@dataclass
class CSATResult:
    """Result after multiple iterations with 7 criteria"""
    # Average scores for each criterion (0-100 scale)
    task_success_avg: float
    helpfulness_relevance_avg: float
    faithfulness_accuracy_avg: float
    empathy_politeness_avg: float
    compliance_safety_avg: float
    efficiency_effort_avg: float
    fluency_coherence_avg: float
    overall_experience_avg: float
    
    # Variance for each criterion
    task_success_variance: float
    helpfulness_relevance_variance: float
    faithfulness_accuracy_variance: float
    empathy_politeness_variance: float
    compliance_safety_variance: float
    efficiency_effort_variance: float
    fluency_coherence_variance: float
    overall_experience_variance: float
    
    # Best explanations
    best_explanations: Dict[str, str]
    
    # Raw model outputs (JSON strings)
    raw_outputs: List[str]
    
    # Ground truth and metrics (1-5 scale)
    ground_truth: Optional[float] = None
    mae: Optional[float] = None
    mse: Optional[float] = None
    rmse: Optional[float] = None
    r2: Optional[float] = None


class CSATPipeline:
    """Main pipeline for CSAT evaluation with 7 criteria"""
    
    def __init__(self, model: BaseCSATModel, num_iterations: int = 5):
        self.model = model
        self.num_iterations = num_iterations
    
    def _convert_100_to_5_scale(self, score_100: float) -> float:
        """Convert 0-100 scale back to 1-5 scale"""
        score_100 = max(0, min(100, score_100))
        return 1 + (score_100 / 100) * 4  # 0→1, 25→2, 50→3, 75→4, 100→5
    
    def evaluate_dialogue(self, dialogue, instruction_prompt: str, rule_based_prompt: str = "") -> CSATResult:
        """Evaluate a single dialogue with multiple iterations"""
        csat_input = CSATInput(
            instruction_prompt=instruction_prompt,
            rule_based_prompt=rule_based_prompt,
            dialogue=dialogue.to_text(),
            language=dialogue.language
        )
        
        outputs = []
        raw_outputs = []
        criteria_scores = {
            'task_success': [],
            'helpfulness_relevance': [],
            'faithfulness_accuracy': [],
            'empathy_politeness': [],
            'compliance_safety': [],
            'efficiency_effort': [],
            'fluency_coherence': [],
            'overall_experience': []
        }
        
        for _ in range(self.num_iterations):
            try:
                # Generate raw response first to capture JSON
                prompt = self.model._construct_prompt(csat_input)
                raw_response = self.model._generate_response(prompt)
                raw_outputs.append(raw_response)
                
                # Parse the response
                output = self.model._parse_output(raw_response)
                outputs.append(output)
                
                # Collect scores for each criterion
                criteria_scores['task_success'].append(output.task_success.score)
                criteria_scores['helpfulness_relevance'].append(output.helpfulness_relevance.score)
                criteria_scores['faithfulness_accuracy'].append(output.faithfulness_accuracy.score)
                criteria_scores['empathy_politeness'].append(output.empathy_politeness.score)
                criteria_scores['compliance_safety'].append(output.compliance_safety.score)
                criteria_scores['efficiency_effort'].append(output.efficiency_effort.score)
                criteria_scores['fluency_coherence'].append(output.fluency_coherence.score)
                criteria_scores['overall_experience'].append(output.overall_experience.score)
                
            except ValueError as e:
                print(f"Configuration/Language error: {e}")
                raise e
            except RuntimeError as e:
                print(f"API error: {e}")
                raise e
            except Exception as e:
                print(f"Unexpected error: {e}")
                raise RuntimeError(f"Unexpected error during evaluation: {str(e)}") from e
        
        # Calculate averages and variances
        averages = {k: float(np.mean(v)) for k, v in criteria_scores.items()}
        variances = {k: float(np.var(v)) for k, v in criteria_scores.items()}
        
        # Select best explanations (closest to average score)
        best_explanations = {}
        for criterion in criteria_scores.keys():
            if outputs:
                scores = criteria_scores[criterion]
                avg_score = averages[criterion]
                best_idx = np.argmin(np.abs(np.array(scores) - avg_score))
                
                if best_idx < len(outputs):
                    output = outputs[best_idx]
                    explanation = getattr(output, criterion).justification
                    best_explanations[criterion] = explanation
                else:
                    best_explanations[criterion] = "No explanation available"
            else:
                best_explanations[criterion] = "No explanation available"
        
        # Calculate metrics using ground truth from OVERALL line
        ground_truth = None
        mae = mse = rmse = r2 = None
        
        # Get ground truth (1-5 scale) and convert model prediction for comparison
        gt_score_1_5 = dialogue.average_satisfaction  # 1-5 scale from OVERALL line
        if gt_score_1_5 is not None:
            ground_truth = gt_score_1_5
            
            # Convert model's overall_experience score from 0-100 to 1-5 scale
            pred_score_100 = averages['overall_experience']  # 0-100 scale
            pred_score_1_5 = self._convert_100_to_5_scale(pred_score_100)  # Convert to 1-5
            
            # Calculate metrics on 1-5 scale
            mae = abs(pred_score_1_5 - gt_score_1_5)
            mse = (pred_score_1_5 - gt_score_1_5) ** 2
            rmse = np.sqrt(mse)
            r2 = 0.0  # Will be calculated at dataset level
        
        return CSATResult(
            task_success_avg=averages['task_success'],
            helpfulness_relevance_avg=averages['helpfulness_relevance'],
            faithfulness_accuracy_avg=averages['faithfulness_accuracy'],
            empathy_politeness_avg=averages['empathy_politeness'],
            compliance_safety_avg=averages['compliance_safety'],
            efficiency_effort_avg=averages['efficiency_effort'],
            fluency_coherence_avg=averages['fluency_coherence'],
            overall_experience_avg=averages['overall_experience'],
            
            task_success_variance=variances['task_success'],
            helpfulness_relevance_variance=variances['helpfulness_relevance'],
            faithfulness_accuracy_variance=variances['faithfulness_accuracy'],
            empathy_politeness_variance=variances['empathy_politeness'],
            compliance_safety_variance=variances['compliance_safety'],
            efficiency_effort_variance=variances['efficiency_effort'],
            fluency_coherence_variance=variances['fluency_coherence'],
            overall_experience_variance=variances['overall_experience'],
            
            best_explanations=best_explanations,
            raw_outputs=raw_outputs,
            ground_truth=ground_truth,
            mae=mae,
            mse=mse,
            rmse=rmse,
            r2=r2
        )


class DatasetExperiment:
    """Run experiments on datasets with 7-criteria evaluation"""
    
    def __init__(self, models: List[BaseCSATModel], num_iterations: int = 5):
        self.models = models
        self.num_iterations = num_iterations
        self.results = {}
    
    def _convert_100_to_5_scale(self, score_100: float) -> float:
        """Convert 0-100 scale back to 1-5 scale"""
        score_100 = max(0, min(100, score_100))
        return 1 + (score_100 / 100) * 4
    
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
        # Get predictions (convert 0-100 to 1-5) and ground truths (already 1-5)
        predictions_1_5 = []
        ground_truths_1_5 = []
        
        for r in results:
            if r.ground_truth is not None:
                pred_100 = r.overall_experience_avg  # 0-100 scale
                pred_1_5 = self._convert_100_to_5_scale(pred_100)  # Convert to 1-5
                
                predictions_1_5.append(pred_1_5)
                ground_truths_1_5.append(r.ground_truth)
        
        metrics = {
            'avg_predicted_score': float(np.mean([r.overall_experience_avg for r in results])),
            'avg_variance': float(np.mean([r.overall_experience_variance for r in results]))
        }
        
        if ground_truths_1_5:
            predictions_1_5 = np.array(predictions_1_5)
            ground_truths_1_5 = np.array(ground_truths_1_5)
            
            # Calculate metrics on 1-5 scale
            mae_values = np.abs(predictions_1_5 - ground_truths_1_5)
            mse_values = (predictions_1_5 - ground_truths_1_5) ** 2
            
            metrics.update({
                'mae': float(np.mean(mae_values)),
                'mse': float(np.mean(mse_values)),
                'rmse': float(np.sqrt(np.mean(mse_values))),
                'avg_pred_1_5': float(np.mean(predictions_1_5)),
                'avg_gt_1_5': float(np.mean(ground_truths_1_5))
            })
            
            # R² calculation
            if len(ground_truths_1_5) > 1:
                ss_res = np.sum(mse_values)
                ss_tot = np.sum((ground_truths_1_5 - np.mean(ground_truths_1_5)) ** 2)
                metrics['r2'] = float(1 - (ss_res / ss_tot)) if ss_tot != 0 else 0.0
                
                # Correlation
                correlation = np.corrcoef(predictions_1_5, ground_truths_1_5)[0, 1]
                metrics['correlation'] = float(correlation) if not np.isnan(correlation) else 0.0
            else:
                metrics['r2'] = 0.0
                metrics['correlation'] = 0.0
        
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
                'MSE': metrics.get('mse', np.nan),
                'RMSE': metrics.get('rmse', np.nan),
                'R²': metrics.get('r2', np.nan),
                'Correlation': metrics.get('correlation', np.nan),
                'Avg_Pred_1_5': metrics.get('avg_pred_1_5', np.nan),
                'Avg_GT_1_5': metrics.get('avg_gt_1_5', np.nan),
                'Avg_Variance': metrics.get('avg_variance', np.nan)
            })
        return pd.DataFrame(summary_data)
    
    def save_organized_results(self, output_dirs: Dict[str, str], plot: bool = False):
        """Save results organized by model"""
        for model_name, output_dir in output_dirs.items():
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            model_results = {k: v for k, v in self.results.items() if v['model_name'] == model_name}
            
            if not model_results:
                continue
            
            # Save summary
            summary_df = self.get_summary()
            model_summary = summary_df[summary_df['Model'] == model_name]
            if not model_summary.empty:
                model_summary.to_csv(output_path / "summary.csv", index=False)
            
            # Save detailed results
            for key, result in model_results.items():
                dataset_name = result['dataset']
                
                # Save raw model outputs (JSON)
                raw_outputs_data = []
                for i, r in enumerate(result['results']):
                    for j, raw_output in enumerate(r.raw_outputs):
                        raw_outputs_data.append({
                            'dialogue_id': i,
                            'iteration': j,
                            'raw_output': raw_output
                        })
                
                with open(output_path / f"{dataset_name}_raw_outputs.json", 'w', encoding='utf-8') as f:
                    json.dump(raw_outputs_data, f, indent=2, ensure_ascii=False)
                
                # Save detailed text report
                with open(output_path / f"{dataset_name}_detailed.txt", 'w', encoding='utf-8') as f:
                    f.write(f"Model: {model_name} | Dataset: {dataset_name}\n")
                    f.write("="*80 + "\n\n")
                    
                    metrics = result['metrics']
                    f.write("Performance Metrics (1-5 Scale Comparison):\n")
                    f.write("-"*50 + "\n")
                    f.write(f"MAE: {metrics.get('mae', 0):.3f}\n")
                    f.write(f"MSE: {metrics.get('mse', 0):.3f}\n")
                    f.write(f"RMSE: {metrics.get('rmse', 0):.3f}\n")
                    f.write(f"R²: {metrics.get('r2', 0):.3f}\n")
                    f.write(f"Correlation: {metrics.get('correlation', 0):.3f}\n")
                    f.write(f"Avg Prediction (1-5): {metrics.get('avg_pred_1_5', 0):.2f}\n")
                    f.write(f"Avg Ground Truth (1-5): {metrics.get('avg_gt_1_5', 0):.2f}\n")
                    f.write(f"Avg Variance: {metrics.get('avg_variance', 0):.3f}\n\n")
                    
                    f.write(f"Sample Results ({len(result['results'])} total):\n")
                    f.write("="*60 + "\n")
                    
                    for i, r in enumerate(result['results'][:5]):  # Show first 5 samples
                        f.write(f"\nSample {i+1}:\n")
                        f.write("-"*30 + "\n")
                        
                        pred_100 = r.overall_experience_avg
                        pred_1_5 = self._convert_100_to_5_scale(pred_100)
                        gt_1_5 = r.ground_truth
                        
                        f.write(f"  Model Score (0-100): {pred_100:.1f}\n")
                        f.write(f"  Model Score (1-5): {pred_1_5:.2f}\n")
                        f.write(f"  Ground Truth (1-5): {gt_1_5:.2f}\n" if gt_1_5 else "  Ground Truth: N/A\n")
                        
                        if gt_1_5 and r.mae:
                            f.write(f"  MAE: {r.mae:.3f}\n")
                            f.write(f"  MSE: {r.mse:.3f}\n")
                            f.write(f"  RMSE: {r.rmse:.3f}\n")
                        
                        f.write(f"  Explanation: {r.best_explanations.get('overall_experience', 'N/A')[:100]}...\n")
                        f.write("\n")
                
                # Save CSV with results
                csv_data = []
                for i, r in enumerate(result['results']):
                    pred_100 = r.overall_experience_avg
                    pred_1_5 = self._convert_100_to_5_scale(pred_100)
                    
                    csv_data.append({
                        'sample_id': i,
                        'predicted_score_100': pred_100,
                        'predicted_score_1_5': pred_1_5,
                        'ground_truth_1_5': r.ground_truth,
                        'mae': r.mae,
                        'mse': r.mse,
                        'rmse': r.rmse,
                        'variance': r.overall_experience_variance,
                        'explanation': r.best_explanations.get('overall_experience', '')[:200]
                    })
                
                pd.DataFrame(csv_data).to_csv(output_path / f"{dataset_name}_results.csv", index=False)
            
            print(f"Results for {model_name} saved to: {output_path}")
            print(f"  - Raw outputs: {dataset_name}_raw_outputs.json")
            print(f"  - Detailed report: {dataset_name}_detailed.txt")
            print(f"  - CSV results: {dataset_name}_results.csv")


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
                        pred_100 = r.overall_experience_avg
                        pred_1_5 = experiment._convert_100_to_5_scale(pred_100)
                        all_predictions.append(pred_1_5)
                        all_ground_truths.append(r.ground_truth)
            
            if not all_predictions:
                return
            
            fig, axes = plt.subplots(2, 2, figsize=(12, 10))
            fig.suptitle(f'CSAT Results - {model_name} (1-5 Scale)', fontsize=16)
            
            # Predictions vs Ground Truth
            axes[0,0].scatter(all_ground_truths, all_predictions, alpha=0.6)
            axes[0,0].plot([1, 5], [1, 5], 'r--', label='Perfect prediction')
            axes[0,0].set_xlabel('Ground Truth (1-5)')
            axes[0,0].set_ylabel('Predicted (1-5)')
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
            variances = [r.overall_experience_variance for result in model_results.values() for r in result['results']]
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
            "CSAT EVALUATION EXPERIMENT REPORT (1-5 Scale Comparison)",
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
                "\nMetrics (1-5 Scale):"
            ])
            
            metrics = result['metrics']
            report.append(f"  MAE: {metrics.get('mae', 0):.4f}")
            report.append(f"  MSE: {metrics.get('mse', 0):.4f}")
            report.append(f"  RMSE: {metrics.get('rmse', 0):.4f}")
            report.append(f"  R²: {metrics.get('r2', 0):.4f}")
            report.append(f"  Correlation: {metrics.get('correlation', 0):.4f}")
            
            report.append("\nSample Predictions (first 3):")
            for i, r in enumerate(result['results'][:3]):
                pred_100 = r.overall_experience_avg
                pred_1_5 = experiment._convert_100_to_5_scale(pred_100)
                report.extend([
                    f"\n  Sample {i+1}:",
                    f"    Predicted (0-100): {pred_100:.1f}",
                    f"    Predicted (1-5): {pred_1_5:.2f}",
                    f"    Ground Truth (1-5): {r.ground_truth:.2f}" if r.ground_truth else "    Ground Truth: N/A",
                    f"    MAE: {r.mae:.3f}" if r.mae else "    MAE: N/A",
                    f"    Explanation: {r.best_explanations.get('overall_experience', 'N/A')[:100]}..."
                ])
        
        return "\n".join(report)
