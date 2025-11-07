"""
LLM 설정 및 팩토리 함수
"""
import os
from functools import lru_cache
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# LLM 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o-mini"

# Temperature 프로파일 (하드코딩된 상수)
TEMPERATURE_DIAGNOSIS = 0.1
TEMPERATURE_RECOMMENDATION_QUERY = 0.1
TEMPERATURE_RECOMMENDATION_SELECT = 0.7
TEMPERATURE_CHAT = 0.7
TEMPERATURE_COSMETIC = 0.1


# LLM 인스턴스 팩토리 (temperature별 캐싱)
@lru_cache(maxsize=8)
def get_llm(temperature: float, model: str = None) -> ChatOpenAI:
    """
    LLM 인스턴스 팩토리 (temperature별 캐싱)
    
    Args:
        temperature: LLM temperature 설정
        model: 모델 이름 (None이면 기본값 사용)
    
    Returns:
        ChatOpenAI: 캐싱된 LLM 인스턴스
    """
    return ChatOpenAI(
        model=model or OPENAI_MODEL,
        temperature=temperature,
        api_key=OPENAI_API_KEY
    )

