"""OpenAI LLM configuration (singleton by temperature).

Provides a cached ChatOpenAI instance keyed by temperature.

Environment Variables:
    - OPENAI_API_KEY: API key for OpenAI-compatible endpoint.
    - OPENAI_MODEL: Model name (default: "gpt-4o-mini").
"""

from __future__ import annotations

import os
from typing import Dict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


load_dotenv()

_LLM_CACHE: Dict[float, ChatOpenAI] = {}


def get_llm(temperature: float = 0.3) -> ChatOpenAI:
    """Return a cached ChatOpenAI instance for the given temperature.

    Args:
        temperature (float): Sampling temperature.

    Returns:
        ChatOpenAI: LLM client instance.

    Raises:
        EnvironmentError: If OPENAI_API_KEY is missing.
    """
    if temperature in _LLM_CACHE:
        return _LLM_CACHE[temperature]

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY가 설정되지 않았습니다. .env를 확인하세요.")

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    llm = ChatOpenAI(
        model=model,
        temperature=temperature,
        api_key=api_key,
    )

    _LLM_CACHE[temperature] = llm
    return llm


__all__ = ["get_llm"]


