from fastapi import status
from sqlalchemy.orm import Session
from app.core.exception import ApiException
from app.repository.like import LikeRepository
from app.repository.cosmetic import CosmeticRepository
from app.services.member import MemberService


class LikeService:
    @staticmethod
    def toggle_like(db: Session, member_id: int, cosmetic_id: int) -> dict:
        """좋아요 토글 + 카운트 반환"""
        # 존재 확인 (개발단계: FK 없음이므로 소프트 체크)
        if not MemberService.exists(db, member_id):
            raise ApiException(status.HTTP_404_NOT_FOUND, "회원을 찾을 수 없습니다")

        if not CosmeticRepository.exists(db, cosmetic_id):
            raise ApiException(status.HTTP_404_NOT_FOUND, "화장품을 찾을 수 없습니다")

        # 토글 실행
        toggle_result = LikeRepository.toggle_like(db, member_id, cosmetic_id)
        
        # 카운트 조회
        like_count = LikeRepository.count_by_cosmetic(db, cosmetic_id)
        
        return {
            "is_liked": toggle_result["is_liked"],
            "like_count": like_count
        }

    @staticmethod
    def get_like_count(db: Session, cosmetic_id: int) -> dict:
        """화장품별 좋아요 개수만 조회"""
        if not CosmeticRepository.exists(db, cosmetic_id):
            raise ApiException(status.HTTP_404_NOT_FOUND, "화장품을 찾을 수 없습니다")
            
        like_count = LikeRepository.count_by_cosmetic(db, cosmetic_id)
        return {"like_count": like_count}

    @staticmethod
    def get_like_info(db: Session, member_id: int, cosmetic_id: int) -> dict:
        """좋아요 여부와 개수 조회"""
        # 존재 확인
        if not MemberService.exists(db, member_id):
            raise ApiException(status.HTTP_404_NOT_FOUND, "회원을 찾을 수 없습니다")

        if not CosmeticRepository.exists(db, cosmetic_id):
            raise ApiException(status.HTTP_404_NOT_FOUND, "화장품을 찾을 수 없습니다")
            
        return LikeRepository.get_like_info(db, member_id, cosmetic_id)
