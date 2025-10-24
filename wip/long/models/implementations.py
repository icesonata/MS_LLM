"""
Model implementations for ChatGPT, Gemini, Qwen, and Mistral - Updated for 7-criteria system with proper error handling
"""

import os
import warnings
from models.base import BaseCSATModel
warnings.filterwarnings('ignore')


class ChatGPTModel(BaseCSATModel):
    """OpenAI ChatGPT implementation"""
    
    def _initialize_model(self):
        try:
            import openai
            if 'model_version' not in self.config:
                raise ValueError("model_version is required for ChatGPT")
            if not self.config.get('api_key'):
                raise ValueError("API key is required for ChatGPT")
            self.client = openai.OpenAI(api_key=self.config['api_key'])
            self.model_version = self.config['model_version']
        except ImportError:
            raise ImportError("OpenAI library not found. Install with: pip install openai")
    
    def _generate_response(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model_version,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config.get('temperature', 0.3),
                max_tokens=self.config.get('max_tokens', 2000)
            )
            
            if not response.choices or not response.choices[0].message.content:
                raise RuntimeError("Empty response received from ChatGPT API")
            
            return response.choices[0].message.content
            
        except Exception as e:
            # Re-raise with more context
            raise RuntimeError(f"ChatGPT API error: {str(e)}") from e


class GeminiModel(BaseCSATModel):
    """Google Gemini implementation"""
    
    def _initialize_model(self):
        try:
            import google.generativeai as genai
            if 'model_version' not in self.config:
                raise ValueError("model_version is required for Gemini")
            if not self.config.get('api_key'):
                raise ValueError("API key is required for Gemini")
                
            genai.configure(api_key=self.config['api_key'])
            self.model = genai.GenerativeModel(self.config['model_version'])
            self.generation_config = genai.types.GenerationConfig(
                temperature=self.config.get('temperature', 0.3),
                max_output_tokens=self.config.get('max_tokens', 16000)
            )
        except ImportError:
            raise ImportError("Google Generative AI library not found. Install with: pip install google-generativeai")
    
    def _generate_response(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt, generation_config=self.generation_config)
            
            if not response.text:
                raise RuntimeError("Empty response received from Gemini API")
            
            return response.text
            
        except Exception as e:
            # Re-raise with more context
            raise RuntimeError(f"Gemini API error: {str(e)}") from e


class QwenModel(BaseCSATModel):
    """Qwen model implementation"""
    
    def _initialize_model(self):
        try:
            import openai
            if 'model_version' not in self.config:
                raise ValueError("model_version is required for Qwen")
            if not self.config.get('api_key'):
                raise ValueError("API key is required for Qwen")
                
            self.client = openai.OpenAI(
                api_key=self.config['api_key'],
                base_url=self.config.get('base_url', 'https://dashscope-intl.aliyuncs.com/compatible-mode/v1'),
            )
            self.model_version = self.config['model_version']
        except ImportError as e:
            raise ImportError(f"OpenAI library required for Qwen. Install with: pip install openai") from e
    
    def _generate_response(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model_version,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config.get('temperature', 0.3),
                max_tokens=self.config.get('max_tokens', 2000),
                extra_body={"enable_thinking": False}
            )
            
            if not response.choices or not response.choices[0].message.content:
                raise RuntimeError("Empty response received from Qwen API")
            
            return response.choices[0].message.content
            
        except Exception as e:
            # Re-raise with more context
            raise RuntimeError(f"Qwen API error: {str(e)}") from e


class MistralModel(BaseCSATModel):
    """Mistral AI implementation - English only"""
    
    def _initialize_model(self):
        try:
            from mistralai import Mistral
            if 'model_version' not in self.config:
                raise ValueError("model_version is required for Mistral")
            if not self.config.get('api_key'):
                raise ValueError("API key is required for Mistral")
                
            self.client = Mistral(api_key=self.config['api_key'])
            self.model_version = self.config['model_version']
        except ImportError:
            raise ImportError("Mistral AI library not found. Install with: pip install mistralai")
    
    def predict(self, input_data):
        """Override predict to check language compatibility"""
        if hasattr(input_data, 'language'):
            from dataloader import Language
            if input_data.language == Language.CHINESE:
                raise ValueError("Mistral does not support Chinese language. Use ChatGPT, Gemini, or Qwen for Chinese datasets.")
        return super().predict(input_data)
    
    def _generate_response(self, prompt: str) -> str:
        # Check for Chinese characters in prompt
        if any('\u4e00' <= char <= '\u9fff' for char in prompt):
            raise ValueError("Chinese text detected in prompt. Mistral only supports English.")
        
        try:
            response = self.client.chat.complete(
                model=self.model_version,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config.get('temperature', 0.3),
                max_tokens=self.config.get('max_tokens', 2000)
            )
            
            if not response.choices or not response.choices[0].message.content:
                raise RuntimeError("Empty response received from Mistral API")
            
            return response.choices[0].message.content
            
        except Exception as e:
            # Re-raise with more context
            raise RuntimeError(f"Mistral API error: {str(e)}") from e
