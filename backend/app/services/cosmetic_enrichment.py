from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from fastapi import status
import logging
from app.core.exception import ApiException
from app.repository.cosmetic import CosmeticRepository
from app.schemas.cosmetic import CosmeticAnalysisResult
from app.utils.prompt import load_prompt
from app.utils.llm import parse_llm_json
from app.core.config.llm import get_llm, TEMPERATURE_COSMETIC
from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)


class CosmeticEnrichmentService:
    """화장품 데이터 보강 서비스 (LLM 기반)"""
    
    @staticmethod
    def _normalize_csv(value: Optional[str], max_items: int | None = None) -> Optional[str]:
        """CSV 형식 문자열 정규화 (중복 제거, 개수 제한)"""
        if value is None:
            return None
        parts = [p.strip() for p in value.split(',') if p.strip()]
        # 중복 제거 (순서 유지)
        seen = set()
        deduped = []
        for p in parts:
            if p not in seen:
                seen.add(p)
                deduped.append(p)
        if max_items is not None:
            deduped = deduped[:max_items]
        return ", ".join(deduped) if deduped else None

    @staticmethod
    def generate_cosmetic_llm_fields(db: Session, cosmetic_id: int) -> Dict[str, Any]:
        """LLM을 호출해 6개 확장 컬럼 값을 생성"""
        base = CosmeticRepository.get_basic_by_id(db, cosmetic_id)
        if not base:
            raise ApiException(status.HTTP_404_NOT_FOUND, "화장품을 찾을 수 없습니다")

        instruction = load_prompt("cosmetic_analysis.yaml")
        filled = instruction.format(
            name=base.get('name', ''),
            brand=base.get('brand', ''),
            short_description=base.get('short_description', ''),
            ingredients=base.get('ingredients', ''),
        )

        # Structured Output을 지원하는 LLM 생성
        llm = get_llm(TEMPERATURE_COSMETIC)
        structured_llm = llm.with_structured_output(CosmeticAnalysisResult)
        
        try:
            # Structured Output 직접 호출
            result = structured_llm.invoke([HumanMessage(content=filled)])
            
            logger.info(f"화장품 분석 완료 (Structured Output): cosmetic_id={cosmetic_id}")
            
            # Pydantic 모델 → dict 변환
            data = {
                'skin_type': result.skin_type,
                'skin_disease': result.skin_disease,
                'main_effect': result.main_effect,
                'care_symptom': result.care_symptom,
                'key_ingredient': result.key_ingredient,
                'description': result.description,
            }
            
        except Exception as e:
            logger.warning(f"Structured Output 실패, 폴백 시도 (cosmetic_id={cosmetic_id}): {e}")
            
            # 폴백: 기존 방식 시도
            try:
                resp = llm.invoke([HumanMessage(content=filled)])
                data = parse_llm_json(resp.content)
                logger.info(f"화장품 분석 완료 (폴백 JSON 파싱): cosmetic_id={cosmetic_id}")
                
            except Exception as fallback_error:
                logger.error(f"폴백도 실패 (cosmetic_id={cosmetic_id}): {fallback_error}")
                raise ApiException(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    f"LLM이 올바른 형식을 반환하지 않았습니다."
                )

        # 정규화
        data_out = {
            'skin_type': CosmeticEnrichmentService._normalize_csv(data.get('skin_type'), max_items=2),
            'skin_disease': CosmeticEnrichmentService._normalize_csv(data.get('skin_disease'), max_items=4),
            'main_effect': CosmeticEnrichmentService._normalize_csv(data.get('main_effect'), max_items=4),
            'care_symptom': CosmeticEnrichmentService._normalize_csv(data.get('care_symptom'), max_items=6),
            'key_ingredient': CosmeticEnrichmentService._normalize_csv(data.get('key_ingredient'), max_items=4),
            'description': (data.get('description') or '').strip() or None,
        }
        return data_out

    @staticmethod
    def enrich_cosmetic_and_save(
        db: Session,
        cosmetic_id: int,
        overwrite: bool = True,
        upsert: bool = True,
    ) -> None:
        """LLM 생성값을 DB에 저장 (덮어쓰기/업서트 정책 지원)"""
        data = CosmeticEnrichmentService.generate_cosmetic_llm_fields(db, cosmetic_id)
        if upsert:
            CosmeticRepository.upsert_llm_fields_mysql(db, cosmetic_id, data, overwrite=overwrite)
        else:
            # 존재하지 않으면 에러, 존재하면 업데이트 수행
            if not CosmeticRepository.exists(db, cosmetic_id):
                raise ApiException(status.HTTP_404_NOT_FOUND, "화장품을 찾을 수 없습니다")
            CosmeticRepository.upsert_llm_fields_mysql(db, cosmetic_id, data, overwrite=overwrite)

