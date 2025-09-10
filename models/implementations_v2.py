"""
Model implementations for ChatGPT, Gemini, Qwen, and Mistral
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
            if 'model_version' not in self.config:
                raise ValueError("model_version is required for ChatGPT")
            self.client = openai.OpenAI(api_key=self.config['api_key'])
            self.model_version = self.config['model_version']
        except ImportError:
            raise ImportError("pip install openai")
    
    def _generate_response(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model_version,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config['temperature'],
                max_tokens=self.config['max_tokens']
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
            if 'model_version' not in self.config:
                raise ValueError("model_version is required for Gemini")
            genai.configure(api_key=self.config['api_key'])
            self.model = genai.GenerativeModel(self.config['model_version'])
            self.generation_config = genai.types.GenerationConfig(
                temperature=self.config['temperature'],
                max_output_tokens=self.config['max_tokens']
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
            if 'model_version' not in self.config:
                raise ValueError("model_version is required for Qwen")
            self.client = openai.OpenAI(
                api_key=self.config['api_key'],
                base_url=self.config.get('base_url', 'https://dashscope-intl.aliyuncs.com/compatible-mode/v1'),
            )
            self.model_version = self.config['model_version']
        except ImportError as e:
            raise ImportError(f"QWEN: Missing dependencies: {e}. Install with: pip install openai")
    
    def _generate_response(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model_version,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config['temperature'],
                max_tokens=self.config['max_tokens'],
                extra_body={"enable_thinking": False}
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"QWEN: error: {e}")
            return "SCORE: 3\nEXPLANATION: Error in generation\nGOLDEN_SYNTHESIS:\n- Sample 1\n- Sample 2\n- Sample 3"


class MistralModel(BaseCSATModel):
    """Mistral AI implementation - English only"""
    
    def _initialize_model(self):
        try:
            from mistralai import Mistral
            if 'model_version' not in self.config:
                raise ValueError("model_version is required for Mistral")
            self.client = Mistral(api_key=self.config['api_key'])
            # Limit HTTP 492: https://github.com/continuedev/continue/issues/6185
            self.model_version = self.config['model_version']
        except ImportError:
            raise ImportError("pip install mistralai")
    
    def predict(self, input_data):
        """Override predict to check language compatibility"""
        if hasattr(input_data, 'language'):
            from dataloader import Language
            if input_data.language == Language.CHINESE:
                return self._parse_output("SCORE: 3\nEXPLANATION: Chinese not supported\nGOLDEN_SYNTHESIS:\n- Use ChatGPT/Gemini\n- English only\n- Language limitation")
        return super().predict(input_data)
    
    def _generate_response(self, prompt: str) -> str:
        try:
            if any('\u4e00' <= char <= '\u9fff' for char in prompt):
                return "SCORE: 3\nEXPLANATION: Chinese not supported\nGOLDEN_SYNTHESIS:\n- English only\n- Use other models\n- Language barrier"
            
            response = self.client.chat.complete(
                model=self.model_version,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config['temperature'],
                max_tokens=self.config['max_tokens']
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Mistral error: {e}")
            return "SCORE: 3\nEXPLANATION: Generation error\nGOLDEN_SYNTHESIS:\n- API issue\n- Try again\n- Check connection"
