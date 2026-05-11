"""LLM integration module for AI recommendations."""

from ai_engine.llm.longcat_client import LongCatClient
from ai_engine.llm.prompts import LLMPrompts
from ai_engine.llm.llm_config import LLMConfig

__all__ = [
    'LongCatClient',
    'LLMPrompts',
    'LLMConfig'
]
