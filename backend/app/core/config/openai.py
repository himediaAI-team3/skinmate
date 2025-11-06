"""OpenAI LLM 설정 (온도별 캐싱).

온도별로 캐시된 ChatOpenAI 인스턴스를 제공합니다.

환경 변수:
    - OPENAI_API_KEY: OpenAI 호환 API 키
    - OPENAI_MODEL: 모델명 (기본값: "gpt-4o-mini")
"""

from __future__ import annotations

import os
from typing import Dict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


load_dotenv()

_LLM_CACHE: Dict[tuple[float, int | None, int | None], ChatOpenAI] = {}


def get_llm(temperature: float = 0.3, max_tokens: int | None = None, timeout: int | None = None) -> ChatOpenAI:
    """지정된 파라미터로 캐시된 ChatOpenAI 인스턴스를 반환합니다.

    Args:
        temperature: 샘플링 온도
        max_tokens: 최대 생성 토큰 수 (None이면 모델 기본값 사용)
        timeout: 요청 타임아웃 (초, None이면 기본값 사용)

    Returns:
        ChatOpenAI: LLM 클라이언트 인스턴스

    Raises:
        EnvironmentError: OPENAI_API_KEY가 없을 때
    """
    cache_key = (temperature, max_tokens, timeout)
    if cache_key in _LLM_CACHE:
        return _LLM_CACHE[cache_key]

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY가 설정되지 않았습니다. .env를 확인하세요.")

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    llm_kwargs = {
        "model": model,
        "temperature": temperature,
        "api_key": api_key,
    }
    if max_tokens is not None:
        llm_kwargs["max_tokens"] = max_tokens
    if timeout is not None:
        llm_kwargs["timeout"] = timeout

    llm = ChatOpenAI(**llm_kwargs)

    _LLM_CACHE[cache_key] = llm
    return llm


__all__ = ["get_llm"]


