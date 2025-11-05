import re
from PIL import Image
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage
from app.repository.diagnosis import DiagnosisRepository
from app.repository.file import FileRepository
from app.models.diagnosis import Diagnosis
from app.models.entity_type import EntityType
from app.utils.image import encode_image_base64
from app.utils.prompt import load_prompt
from app.core.config.llm import get_llm, TEMPERATURE_DIAGNOSIS
from app.core.exception.exceptions import ApiException
from fastapi import status as http_status
import logging

logger = logging.getLogger(__name__)


class DiagnosisService:
    
    @staticmethod
    def create_diagnosis(db: Session, analysis_id: int) -> Diagnosis:
        
        # analysis_id로 파일 조회
        file = FileRepository.get_by_entity(db, EntityType.SKIN_ANALYSIS, analysis_id)
        logger.info(f"진단 시작: analysis_id={analysis_id}, file_path={file.file_path}")

        # 이미지 로드 및 Base64 인코딩
        image = Image.open(file.file_path).convert("RGB")
        image_base64 = encode_image_base64(image)
        logger.info(f"이미지 Base64 인코딩 완료 (길이: {len(image_base64)}자)")

        # 프롬프트 로드
        instruction = load_prompt("diagnosis.yaml")

        # ==================== 런팟 파인튜닝 모델 호출 ====================
        # # Vision 모델 초기화
        # llm = ChatOpenAI(
        #     model=os.getenv("RUNPOD_MODEL_NAME"),
        #     api_key=os.getenv("RUNPOD_API_KEY"),
        #     base_url=os.getenv("RUNPOD_BASE_URL"),
        #     temperature=0.1,
        # )
        # 
        # # 메시지 구성
        # messages = [
        #     HumanMessage(
        #         content=[
        #             {"type": "text", "text": instruction},
        #             {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
        #         ]
        #     )
        # ]
        # 
        # try:
        #     logger.info("런팟 Vision 모델 호출 시작...")
        #     response = llm.invoke(messages)
        #     logger.info("런팟 Vision 모델 응답 수신 완료")
        # ================================================================

        # OpenAI Vision API 호출
        llm = get_llm(TEMPERATURE_DIAGNOSIS)

        # 메시지 구성
        messages = [
            HumanMessage(
                content=[
                    {"type": "text", "text": instruction},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                ]
            )
        ]

        try:
            logger.info("OpenAI Vision API 호출 시작...")
            response = llm.invoke(messages)
            logger.info("OpenAI Vision API 응답 수신 완료")
            
            # 결과 파싱
            disease = re.search(r"<label>(.*?)</label>", response.content)
            summary = re.search(r"<summary>(.*?)</summary>", response.content)
            
            if not disease or not summary:
                raise ApiException(http_status.HTTP_500_INTERNAL_SERVER_ERROR,"AI 진단 응답 형식이 올바르지 않습니다")
            
            disease_name = disease.group(1)
            #     logger.info(f"런팟 Vision 모델 진단 완료: disease_name={disease_name}")
            logger.info(f"OpenAI Vision API 진단 완료: disease_name={disease_name}")
            
            diagnosis_data = {
                "analysis_id": analysis_id,
                "disease_name": disease_name,
                "summary": summary.group(1)
            }
            
        except ApiException:
            raise
            
        except Exception as e:
            raise ApiException(
                http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                f"AI 진단 중 오류가 발생했습니다: {str(e)}"
            )
        
        # 에러 없을 때만 DB에 저장
        return DiagnosisRepository.create(db, diagnosis_data)