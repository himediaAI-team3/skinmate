"""OpenAI(LangChain) LLM 설정"""
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


# 서버 프로세스에서도 확실히 로드되도록 backend/.env 명시 로드
_backend_env = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(_backend_env)


class OpenAIConfig:
    """OpenAI Chat 모델 설정 및 싱글톤 제공"""

    MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    API_KEY = os.getenv("OPENAI_API_KEY")

    _chat_client: ChatOpenAI | None = None

    @classmethod
    def get_chat_client(cls) -> ChatOpenAI:
        if cls._chat_client is None:
            kwargs = {
                "model": cls.MODEL,
                "api_key": cls.API_KEY,
                "temperature": 0.2,
            }


            cls._chat_client = ChatOpenAI(**kwargs)
        return cls._chat_client


# 싱글톤 인스턴스
llm_client = OpenAIConfig.get_chat_client()


