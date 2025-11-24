import os
import json
import time
from typing import List, Dict, Any

class QwenModel:
    def __init__(self, model_version: str = "qwen3-30b-a3b-instruct-2507"):
        try:
            import openai
        except ImportError:
            raise ImportError("OpenAI library required. Install with: pip install openai")
            
        self.api_key = os.getenv('QWEN_API_KEY')
        if not self.api_key:
            raise ValueError("QWEN_API_KEY environment variable is not set")
            
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url='https://dashscope-intl.aliyuncs.com/compatible-mode/v1',
        )
        self.model_version = model_version

    def generate(self, prompt: str, temperature: float = 0.3, max_tokens: int = 2000) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model_version,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                extra_body={"enable_thinking": True}
            )
            
            if not response.choices or not response.choices[0].message.content:
                return "Error: Empty response"
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error: {str(e)}"

def load_dataset(file_path: str) -> List[Dict]:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('dialogues', [])

def format_dialogue(turns: List[Dict]) -> str:
    formatted = []
    for turn in turns:
        speaker = turn.get('speaker', 'UNKNOWN')
        text = turn.get('text', '')
        formatted.append(f"{speaker}: {text}")
    return "\n".join(formatted)

def load_prompt(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()
