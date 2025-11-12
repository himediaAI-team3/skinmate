"""
질환 Q&A 서비스: RAG 기반 질환 정보 검색 및 답변 생성
"""
from typing import List, Dict, Any
import logging
from langchain_core.messages import HumanMessage, SystemMessage
from app.services.vector_store import VectorStoreService
from app.core.config.llm import get_llm, TEMPERATURE_CHAT

logger = logging.getLogger(__name__)


class DiseaseQAService:
    """질환 Q&A 서비스"""
    
    @staticmethod
    def search_relevant_info(user_question: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        사용자 질문과 관련된 전문 정보 검색
        
        Args:
            user_question: 사용자 질문
            top_k: 검색할 최대 청크 개수
            
        Returns:
            List[Dict[str, Any]]: 검색된 청크 리스트
        """
        try:
            results = VectorStoreService.search_disease_qa(
                query_text=user_question,
                limit=top_k
            )
            logger.info(f"질환 Q&A 검색 완료: {len(results)}개 청크 발견")
            return results
        except Exception as e:
            logger.error(f"질환 Q&A 검색 실패: {e}")
            return []
    
    @staticmethod
    def generate_answer(user_question: str, relevant_chunks: List[Dict[str, Any]]) -> str:
        """
        검색된 정보를 기반으로 LLM이 답변 생성
        
        Args:
            user_question: 사용자 질문
            relevant_chunks: 검색된 관련 청크 리스트
            
        Returns:
            str: LLM이 생성한 답변
        """
        if not relevant_chunks:
            return "죄송합니다. 질문에 대한 전문 정보를 찾을 수 없습니다. 다른 질문을 시도해보세요."
        
        # 컨텍스트 구성
        context_parts = []
        for i, chunk in enumerate(relevant_chunks, 1):
            disease_name = chunk.get("disease_name", "알 수 없음")
            chunk_text = chunk.get("chunk_text", "")
            context_parts.append(f"[{disease_name} 관련 정보 {i}]\n{chunk_text}")
        
        context = "\n\n".join(context_parts)
        
        # 시스템 프롬프트
        system_prompt = """당신은 피부질환 전문 상담사입니다. 사용자의 질문에 대해 제공된 전문 정보를 바탕으로 정확하고 도움이 되는 답변을 제공하세요.

주의사항:
- 제공된 전문 정보를 기반으로만 답변하세요.
- 정보가 부족하거나 불확실한 경우, 추측하지 말고 그렇게 말하세요.
- 답변은 친절하고 이해하기 쉽게 작성하세요.
- 전문 정보의 출처(질환명)를 명시하세요."""
        
        # 사용자 프롬프트
        user_prompt = f"""다음 전문 정보를 바탕으로 사용자 질문에 답변해주세요.

전문 정보:
{context}

사용자 질문: {user_question}

답변:"""
        
        try:
            llm = get_llm(TEMPERATURE_CHAT)
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            response = llm.invoke(messages)
            answer = response.content.strip()
            logger.info(f"질환 Q&A 답변 생성 완료: {len(answer)}자")
            return answer
        except Exception as e:
            logger.error(f"질환 Q&A 답변 생성 실패: {e}")
            return "죄송합니다. 답변 생성 중 오류가 발생했습니다."
    
    @staticmethod
    def search_and_answer(user_question: str, top_k: int = 5) -> str:
        """
        사용자 질문에 대한 전문 정보 검색 및 답변 생성 (통합 메서드)
        
        Args:
            user_question: 사용자 질문
            top_k: 검색할 최대 청크 개수
            
        Returns:
            str: LLM이 생성한 답변
        """
        # 1. 관련 정보 검색
        relevant_chunks = DiseaseQAService.search_relevant_info(user_question, top_k=top_k)
        
        # 2. 답변 생성
        answer = DiseaseQAService.generate_answer(user_question, relevant_chunks)
        
        return answer

