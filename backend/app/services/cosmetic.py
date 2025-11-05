from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from fastapi import status
from app.core.exception import ApiException
from app.repository.cosmetic import CosmeticRepository
from app.schemas.cosmetic import CosmeticSearchParams, CosmeticSearchResponse, CosmeticSearchItem, CosmeticDetailResponse
from app.utils.prompt import load_prompt
from app.utils.llm import parse_llm_json
from app.core.config.llm import get_llm, TEMPERATURE_COSMETIC
from langchain_core.messages import HumanMessage


class CosmeticService:
    
    @staticmethod
    def search_cosmetics(
        db: Session,
        params: CosmeticSearchParams
    ) -> CosmeticSearchResponse:
        """화장품 목록 검색"""
        
        # 리포지토리에서 데이터 조회
        items_data, total = CosmeticRepository.search(
            db=db,
            brand=params.brand,
            name=params.name,
            skin_type=params.skin_type,
            category=params.category,
            member_id=params.member_id,
            page=params.page,
            size=params.size
        )
        
        # 스키마로 변환
        items = [CosmeticSearchItem(**item) for item in items_data]
        
        return CosmeticSearchResponse(
            page=params.page,
            size=params.size,
            total=total,
            items=items
        )
    
    @staticmethod
    def get_cosmetic_detail(
        db: Session,
        cosmetic_id: int,
        member_id: Optional[int] = None
    ) -> CosmeticDetailResponse:
        """화장품 상세 정보 조회"""
        
        # 리포지토리에서 데이터 조회
        data = CosmeticRepository.get_detail(db, cosmetic_id, member_id)
        
        # 데이터가 없으면 404 에러
        if not data:
            raise ApiException(status.HTTP_404_NOT_FOUND, "화장품을 찾을 수 없습니다")
        
        # 스키마로 변환하여 반환
        return CosmeticDetailResponse(**data)

    @staticmethod
    def _normalize_csv(value: Optional[str], max_items: int | None = None) -> Optional[str]:
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
    def generate_cosmetic_llm_fields(db: Session, cosmetic_id: int) -> Dict[str, Any]:  # LLM 생성값으로 기존 6개 컬럼 덮어쓰기
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

        llm = get_llm(TEMPERATURE_COSMETIC)
        messages = [HumanMessage(content=filled)]
        resp = llm.invoke(messages)
        data = parse_llm_json(resp.content)

        # 정규화
        data_out = {
            'skin_type': CosmeticService._normalize_csv(data.get('skin_type'), max_items=2),
            'skin_disease': CosmeticService._normalize_csv(data.get('skin_disease'), max_items=4),
            'main_effect': CosmeticService._normalize_csv(data.get('main_effect'), max_items=4),
            'care_symptom': CosmeticService._normalize_csv(data.get('care_symptom'), max_items=6),
            'key_ingredient': CosmeticService._normalize_csv(data.get('key_ingredient'), max_items=4),
            'description': (data.get('description') or '').strip() or None,
        }
        return data_out

    @staticmethod
    def enrich_cosmetic_and_save(  # LLM 생성값으로 기존 6개 컬럼 덮어쓰기
        db: Session,
        cosmetic_id: int,
        overwrite: bool = True,
        upsert: bool = True,
    ) -> None:
        """LLM 생성값을 DB에 저장 (덮어쓰기/업서트 정책 지원)"""
        data = CosmeticService.generate_cosmetic_llm_fields(db, cosmetic_id)
        if upsert:
            CosmeticRepository.upsert_llm_fields_mysql(db, cosmetic_id, data, overwrite=overwrite)
        else:
            # 존재하지 않으면 에러, 존재하면 업데이트 수행
            if not CosmeticRepository.exists(db, cosmetic_id):
                raise ApiException(status.HTTP_404_NOT_FOUND, "화장품을 찾을 수 없습니다")
            CosmeticRepository.upsert_llm_fields_mysql(db, cosmetic_id, data, overwrite=overwrite)
