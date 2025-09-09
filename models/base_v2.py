"""
Base model interface for CSAT evaluation
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import re
from dataloader import Language


@dataclass
class CSATInput:
    instruction_prompt: str
    rule_based_prompt: str
    dialogue: str
    language: Language


@dataclass
class CSATOutput:
    score: int
    explanation: str
    golden_synthesis: List[str]
    confidence: Optional[float] = None


class BaseCSATModel(ABC):
    def __init__(self, model_name: str, config: Dict[str, Any] = None):
        self.model_name = model_name
        self.config = config or {}
        self._initialize_model()
    
    @abstractmethod
    def _initialize_model(self): pass
    
    @abstractmethod
    def _generate_response(self, prompt: str) -> str: pass
    
    def predict(self, input_data: CSATInput) -> CSATOutput:
        prompt = self._construct_prompt(input_data)
        response = self._generate_response(prompt)
        return self._parse_output(response)
    
    def _construct_prompt(self, input_data: CSATInput) -> str:
        template = self._get_template(input_data.language)
        return template.format(
            instruction=input_data.instruction_prompt,
            rules=input_data.rule_based_prompt or "No specific rules provided.",
            dialogue=input_data.dialogue
        )
    
    def _get_template(self, language: Language) -> str:
        templates = {
            Language.CHINESE: """
任务：客户满意度评估
{instruction}
评估指南：{rules}
客户服务对话：{dialogue}

请提供：
1. CSAT评分（1-5分）：1=非常不满意，2=不满意，3=中立，4=满意，5=非常满意
2. 详细解释
3. 3个参考样本

格式：
评分：[1-5]
解释：[详细解释]
黄金综合样本：
- [样本1]
- [样本2]
- [样本3]
""",
            Language.ENGLISH: """
Task: Customer Satisfaction Evaluation
{instruction}
Guidelines: {rules}
Dialogue: {dialogue}

Provide:
1. CSAT Score (1-5): 1=Very Dissatisfied, 2=Dissatisfied, 3=Neutral, 4=Satisfied, 5=Very Satisfied
2. Detailed explanation
3. 3 reference samples

Format:
SCORE: [1-5]
EXPLANATION: [detailed explanation]
GOLDEN_SYNTHESIS:
- [Sample 1]
- [Sample 2]
- [Sample 3]
"""
        }
        return templates.get(language, templates[Language.ENGLISH])
    
    def _parse_output(self, response: str) -> CSATOutput:
        # Extract score
        score_match = re.search(r'(?:SCORE|评分)[：:\s]*(\d)', response, re.IGNORECASE)
        score = int(score_match.group(1)) if score_match else 3
        score = max(1, min(5, score))
        
        # Extract explanation
        exp_match = re.search(r'(?:EXPLANATION|解释)[：:\s]*(.+?)(?=GOLDEN|黄金|$)', response, re.DOTALL | re.IGNORECASE)
        explanation = exp_match.group(1).strip() if exp_match else "No explanation provided"
        
        # Extract golden synthesis
        syn_match = re.search(r'(?:GOLDEN_SYNTHESIS|黄金综合样本)[：:\s]*(.+?)$', response, re.DOTALL | re.IGNORECASE)
        golden_synthesis = []
        if syn_match:
            samples = re.findall(r'[-•]\s*(.+?)(?=\n[-•]|$)', syn_match.group(1), re.DOTALL)
            golden_synthesis = [s.strip() for s in samples if s.strip()][:3]
        
        return CSATOutput(
            score=score,
            explanation=explanation,
            golden_synthesis=golden_synthesis or ["No samples provided"]
        )
