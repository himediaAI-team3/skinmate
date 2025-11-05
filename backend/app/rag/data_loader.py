from __future__ import annotations

from typing import Dict, Optional

from sqlalchemy.orm import Session

from app.repository.analysis import AnalysisRepository
from app.repository.diagnosis import DiagnosisRepository


def load_diagnosis_info(db: Session, analysis_id: int) -> Dict[str, Optional[object]]:
    """analysis_id로 진단/사용자 선호 정보를 조회합니다.

    Returns:
        {"disease_name", "summary", "skin_type", "min_price", "max_price"}

    예외:
        분석/진단 데이터가 없으면 ValueError
    """

    analysis = AnalysisRepository.get_by_id(db, analysis_id)
    if not analysis:
        raise ValueError("분석 결과를 찾을 수 없습니다")

    diagnosis = DiagnosisRepository.get_by_analysis_id(db, analysis_id)
    if not diagnosis:
        raise ValueError("진단 정보를 찾을 수 없습니다")

    return {
        "disease_name": diagnosis.disease_name or "",
        "summary": diagnosis.summary or "",
        "skin_type": analysis.skin_type,
        "min_price": analysis.min_price,
        "max_price": analysis.max_price,
    }


__all__ = ["load_diagnosis_info"]


