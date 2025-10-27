"""Utility helpers for interacting with OpenAI Chat API.

Ensures the API key is loaded each process invocation (reading key.txt if the
OPENAI_API_KEY env var is absent) so that individual script runs don't rely on
calling get_key.py beforehand.

Uses the OpenAI >=1.0 client interface.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import List, Dict, Any
import yaml

try:
    # OpenAI >= 1.x
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None  # type: ignore


ROOT = Path(__file__).resolve().parents[1]
KEY_FILE = ROOT / "key.txt"


_client = None


def ensure_api_key() -> str:
    key = os.environ.get("OPENAI_API_KEY")
    if key:
        return key
    if KEY_FILE.exists():
        key = KEY_FILE.read_text(encoding="utf-8").strip()
        if key:
            os.environ["OPENAI_API_KEY"] = key
            return key
    raise RuntimeError(
        "OPENAI_API_KEY not set and key.txt not found or empty. Place your key in key.txt (first line) or export OPENAI_API_KEY."
    )


def get_client():
    global _client
    if _client is None:
        ensure_api_key()
        if OpenAI is None:
            raise RuntimeError("openai package (>=1.0) not installed.")
        _client = OpenAI()
    return _client


def call_chat(messages: List[Dict[str, str]], model: str = "gpt-4o-mini", temperature: float = 0.0, max_tokens: int = 800) -> str:
    """Call OpenAI chat completion and return content string.

    Parameters
    ----------
    messages: list of {role, content}
    model: model name
    temperature: sampling temperature
    max_tokens: response token cap
    """
    client = get_client()
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return (response.choices[0].message.content or "").strip()


def simple_user_prompt(prompt: str, **kwargs) -> str:
    """Call chat with a single-user prompt, using defaults from configs/config.yaml.

    Keyword args override values from the config file. Expected llm defaults in
    the YAML under the `llm` key (model, temperature, max_tokens).
    """
    # Load defaults from configs/config_gpt4_1.yaml if available
    config_path = ROOT / "configs" / "config_gpt4_1.yaml"
    defaults: Dict[str, Any] = {}
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as fh:
                cfg = yaml.safe_load(fh) or {}
            defaults = cfg.get("llm", {}) if isinstance(cfg, dict) else {}
        except Exception:
            # If YAML parsing fails, silently fall back to hardcoded defaults
            defaults = {}

    # Map YAML keys to call_chat kwargs
    call_kwargs: Dict[str, Any] = {}
    if "model" in defaults:
        call_kwargs["model"] = defaults["model"]
    if "temperature" in defaults:
        call_kwargs["temperature"] = defaults["temperature"]
    if "max_tokens" in defaults:
        call_kwargs["max_tokens"] = defaults["max_tokens"]

    # Allow explicit kwargs to override config defaults
    call_kwargs.update(kwargs)

    return call_chat([{"role": "user", "content": prompt}], **call_kwargs)
