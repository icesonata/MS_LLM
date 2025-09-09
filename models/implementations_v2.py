"""
Model implementations for ChatGPT, Gemini, and Qwen
"""

import os
from models.base import BaseCSATModel
import warnings
warnings.filterwarnings('ignore')


class ChatGPTModel(BaseCSATModel):
    """OpenAI ChatGPT implementation"""
    
    def _initialize_model(self):
        try:
            import openai
            self.client = openai.OpenAI(api_key=self.config.get('api_key', os.getenv('OPENAI_API_KEY')))
            self.model_version = self.config.get('model_version', 'gpt-4o')
        except ImportError:
            raise ImportError("pip install openai")
    
    def _generate_response(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model_version,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config.get('temperature', 0.3),
                max_tokens=self.config.get('max_tokens', 1000)
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"ChatGPT error: {e}")
            return "SCORE: 3\nEXPLANATION: Error in generation\nGOLDEN_SYNTHESIS:\n- Sample 1\n- Sample 2\n- Sample 3"


class GeminiModel(BaseCSATModel):
    """Google Gemini implementation"""
    
    def _initialize_model(self):
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.config.get('api_key', os.getenv('GEMINI_API_KEY')))
            self.model = genai.GenerativeModel(self.config.get('model_version', 'gemini-2.0-flash'))
            self.generation_config = genai.types.GenerationConfig(
                temperature=self.config.get('temperature', 0.3),
                max_output_tokens=self.config.get('max_tokens', 1000)
            )
        except ImportError:
            raise ImportError("pip install google-generativeai")
    
    def _generate_response(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt, generation_config=self.generation_config)
            return response.text or self._get_default_response()
        except Exception as e:
            print(f"Gemini error: {e}")
            return self._get_default_response()
    
    def _get_default_response(self):
        return "SCORE: 3\nEXPLANATION: Error in generation\nGOLDEN_SYNTHESIS:\n- Sample 1\n- Sample 2\n- Sample 3"


class QwenModel(BaseCSATModel):
    """Qwen model implementation"""
    
    def _initialize_model(self):
        try:
            import openai
            self.client = openai.OpenAI(
                api_key=self.config.get('api_key', os.getenv('QWEN_API_KEY')),
                base_url=self.config.get('base_url', 'https://dashscope-intl.aliyuncs.com/compatible-mode/v1'),
            )
            self.model_version = self.config.get('model_version', 'qwen3-8b')  # Default to qwen3-8b

        except ImportError as e:
            raise ImportError(f"QWEN: Missing dependencies: {e}. Install with: pip install openai")
    
    def _generate_response(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model_version,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config.get('temperature', 0.3),
                max_tokens=self.config.get('max_tokens', 1000),
                extra_body={"enable_thinking": False}  # Required for Qwen API
            )
            return response.choices[0].message.content
                
        except Exception as e:
            print(f"QWEN: error: {e}")
            return "SCORE: 3\nEXPLANATION: Error in generation\nGOLDEN_SYNTHESIS:\n- Sample 1\n- Sample 2\n- Sample 3"
