from enum import Enum


class EntityType(str, Enum):
    """파일 조회시 엔티티 타입 (entity_type)"""
    SKIN_ANALYSIS = "skin_analysis"
    COSMETIC = "cosmetic"