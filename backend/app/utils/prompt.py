import os
import yaml


def load_prompt(file_name: str) -> str:
    """프롬프트 파일을 로드하여 instruction을 반환"""
    # 현재 파일의 위치를 기준으로 절대 경로 계산
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(os.path.dirname(current_dir))  # backend/app 상위
    path = os.path.join(base_dir, "app", "core", "prompt", file_name)
    
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)["instruction"]
