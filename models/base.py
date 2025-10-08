"""
Base model interface for CSAT evaluation with 7-criteria scoring
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import json
import re
from dataloader import Language


@dataclass
class CSATInput:
    instruction_prompt: str
    rule_based_prompt: str
    dialogue: str
    language: Language


@dataclass
class CriteriaScore:
    score: int
    justification: str


@dataclass
class CSATOutput:
    task_success: CriteriaScore
    helpfulness_relevance: CriteriaScore
    faithfulness_accuracy: CriteriaScore
    empathy_politeness: CriteriaScore
    compliance_safety: CriteriaScore
    efficiency_effort: CriteriaScore
    fluency_coherence: CriteriaScore
    overall_experience: CriteriaScore
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
            dialogue_transcript=input_data.dialogue
        )
    
    def _get_template(self, language: Language) -> str:
        # For now, using English template - can be extended for other languages
        return """
You are an evaluator for customer service dialogues. 
Your task is to score the following transcript according to 7 criteria, each from 0 (worst) to 100 (best).

1. **TaskSuccess**  
   - Was the customer's issue resolved correctly and completely?  
   - Did the agent/system provide accurate and actionable next steps?  

2. **HelpfulnessRelevance**  
   - Were the responses useful, specific, and relevant to the customer's query?  
   - Did the agent/system avoid unnecessary or generic replies?  

3. **FaithfulnessAccuracy**  
   - Are all responses factually correct and grounded in available data, policies, or documents?  
   - Is there any sign of hallucination, misinformation, or unsupported claims?  

4. **EmpathyPoliteness**  
   - Does the agent/system acknowledge the customer's concerns, show understanding, and use polite, professional tone?  
   - Is there emotional appropriateness (e.g., apology, reassurance)?  

5. **ComplianceSafety**  
   - Does the dialogue avoid disallowed actions (e.g., PII leakage, unsafe advice, policy violations)?  
   - Does it follow organizational rules and escalation guidelines?  

6. **EfficiencyEffort**  
   - Was the solution provided in a concise way with minimal back-and-forth?  
   - Did the dialogue reduce customer effort (low repetition, clear instructions)?  

7. **FluencyCoherence**  
   - Are sentences grammatically correct, natural, and easy to understand?  
   - Does the conversation flow logically without contradictions or abrupt shifts?  

---

=== Final Output: ===
- Assign individual scores for each criterion (0–100).
- Provide a **brief justification** for each score.
- Based on the criteria, justify **OverallExperience**, how satisfied would the customer likely be?

Expected Output strictly in JSON format:
{{
  "TaskSuccess": {{"score": <int>, "justification": "<short explanation>"}},
  "HelpfulnessRelevance": {{"score": <int>, "justification": "<short explanation>"}},
  "FaithfulnessAccuracy": {{"score": <int>, "justification": "<short explanation>"}},
  "EmpathyPoliteness": {{"score": <int>, "justification": "<short explanation>"}},
  "ComplianceSafety": {{"score": <int>, "justification": "<short explanation>"}},
  "EfficiencyEffort": {{"score": <int>, "justification": "<short explanation>"}},
  "FluencyCoherence": {{"score": <int>, "justification": "<short explanation>"}},
  "OverallExperience": {{"score": <int>, "justification": "<explain how it was calculated>"}}
}}

=== Customer Service Dialogue ===

{dialogue_transcript}
---

=== Now evaluate the following dialogue ===
"""
    
    def _parse_output(self, response: str) -> CSATOutput:
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if not json_match:
                return self._create_fallback_output("No JSON found in response")
            
            json_str = json_match.group(0)
            data = json.loads(json_str)
            
            # Parse each criteria
            criteria_mapping = {
                'TaskSuccess': 'task_success',
                'HelpfulnessRelevance': 'helpfulness_relevance',
                'FaithfulnessAccuracy': 'faithfulness_accuracy',
                'EmpathyPoliteness': 'empathy_politeness',
                'ComplianceSafety': 'compliance_safety',
                'EfficiencyEffort': 'efficiency_effort',
                'FluencyCoherence': 'fluency_coherence',
                'OverallExperience': 'overall_experience'
            }
            
            parsed_criteria = {}
            for json_key, attr_name in criteria_mapping.items():
                if json_key in data:
                    score = self._validate_score(data[json_key].get('score', 50))
                    justification = data[json_key].get('justification', 'No justification provided')
                    parsed_criteria[attr_name] = CriteriaScore(score=score, justification=justification)
                else:
                    parsed_criteria[attr_name] = CriteriaScore(score=50, justification='Criteria not found in response')
            
            return CSATOutput(**parsed_criteria)
            
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            return self._create_fallback_output(f"Error parsing JSON: {str(e)}")
    
    def _validate_score(self, score: Any) -> int:
        """Validate and clamp score to 0-100 range"""
        try:
            score_int = int(score)
            return max(0, min(100, score_int))
        except (ValueError, TypeError):
            return 50  # Default fallback score
    
    def _create_fallback_output(self, error_msg: str) -> CSATOutput:
        """Create a fallback output when parsing fails"""
        fallback_criteria = CriteriaScore(score=50, justification=f"Parsing failed: {error_msg}")
        
        return CSATOutput(
            task_success=fallback_criteria,
            helpfulness_relevance=fallback_criteria,
            faithfulness_accuracy=fallback_criteria,
            empathy_politeness=fallback_criteria,
            compliance_safety=fallback_criteria,
            efficiency_effort=fallback_criteria,
            fluency_coherence=fallback_criteria,
            overall_experience=fallback_criteria
        )
