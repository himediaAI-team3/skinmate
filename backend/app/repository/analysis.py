from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.skin_analysis import SkinAnalysis
from app.models.diagnosis import Diagnosis
from app.models.entity_type import EntityType
from app.repository.file import FileRepository
from app.repository.diagnosis import DiagnosisRepository
from app.repository.recommendation import RecommendationRepository


class AnalysisRepository:
    
    @staticmethod
    def create(db: Session, analysis_data: dict) -> SkinAnalysis:
        """피부 분석 생성"""
        analysis = SkinAnalysis(**analysis_data)
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        return analysis
    
    @staticmethod
    def get_by_id(db: Session, analysis_id: int) -> SkinAnalysis:
        return db.query(SkinAnalysis).filter(SkinAnalysis.analysis_id == analysis_id).first()
    
    @staticmethod
    def get_by_member_id_with_pagination(db: Session, member_id: int, page: int = 1, size: int = 10, 
                                       disease_name: str = None, period: str = "all"):
        """특정 사용자의 분석 이력을 페이징하여 조회 (최신순)"""
        offset = (page - 1) * size
        
        # 기본 쿼리
        query = db.query(
            SkinAnalysis.analysis_id,
            Diagnosis.disease_name,
            SkinAnalysis.created_at
        ).join(
            Diagnosis, SkinAnalysis.analysis_id == Diagnosis.analysis_id
        ).filter(
            SkinAnalysis.member_id == member_id
        )
        
        # 진단명 필터링
        if disease_name:
            query = query.filter(Diagnosis.disease_name.ilike(f"%{disease_name}%"))
        
        # 기간 필터링
        if period != "all":
            now = datetime.now()
            if period == "day":
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif period == "week":
                start_date = now - timedelta(days=7)
            elif period == "month":
                start_date = now - timedelta(days=30)
            else:
                start_date = None
            
            if start_date:
                query = query.filter(SkinAnalysis.created_at >= start_date)
        
        return query.order_by(
            SkinAnalysis.created_at.desc()
        ).offset(offset).limit(size).all()
    
    @staticmethod
    def count_by_member_id(db: Session, member_id: int, disease_name: str = None, period: str = "all") -> int:
        """특정 사용자의 분석 이력 개수 (필터링 조건 반영)"""
        # 기본 쿼리
        query = db.query(SkinAnalysis).join(
            Diagnosis, SkinAnalysis.analysis_id == Diagnosis.analysis_id
        ).filter(
            SkinAnalysis.member_id == member_id
        )
        
        # 진단명 필터링
        if disease_name:
            query = query.filter(Diagnosis.disease_name.ilike(f"%{disease_name}%"))
        
        # 기간 필터링
        if period != "all":
            now = datetime.now()
            if period == "day":
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif period == "week":
                start_date = now - timedelta(days=7)
            elif period == "month":
                start_date = now - timedelta(days=30)
            else:
                start_date = None
            
            if start_date:
                query = query.filter(SkinAnalysis.created_at >= start_date)
        
        return query.count()
    
    @staticmethod
    def delete_by_id(db: Session, analysis_id: int) -> bool:
        """분석 이력 삭제 (연관 데이터도 함께 삭제)"""
        # 1. skin_analysis 존재 확인
        analysis = db.query(SkinAnalysis).filter(SkinAnalysis.analysis_id == analysis_id).first()
        if not analysis:
            return False
        
        # 2. 관련 file 데이터 삭제
        FileRepository.delete_by_entity(db, EntityType.SKIN_ANALYSIS, analysis_id)
        
        # 3. 관련 diagnosis 데이터 삭제
        DiagnosisRepository.delete_by_analysis_id(db, analysis_id)
        
        # 4. 관련 recommendation 데이터 삭제
        RecommendationRepository.delete_by_analysis_id(db, analysis_id)
        
        # 5. skin_analysis 삭제
        db.delete(analysis)
        return True
    

