from __future__ import annotations

from typing import Dict, Optional

from sqlalchemy.orm import Session

from app.repository.analysis import AnalysisRepository
from app.repository.diagnosis import DiagnosisRepository


def load_diagnosis_info(db: Session, analysis_id: int) -> Dict[str, Optional[object]]:
    """Load diagnosis and user preference info by analysis_id.

    Args:
        db (Session): SQLAlchemy session injected by caller.
        analysis_id (int): Skin analysis identifier.

    Returns:
        Dict[str, Optional[object]]: Dictionary containing disease and user context.
            {
                "disease_name": str,
                "summary": str,
                "skin_type": str | None,
                "min_price": int | None,
                "max_price": int | None,
            }

    Raises:
        ValueError: If analysis or diagnosis record is missing.
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


