import os
import yaml


def load_prompt(file_name: str) -> str:
    """프롬프트 파일을 로드하여 instruction을 반환"""
    path = os.path.join("app/core/prompt", file_name)
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)["instruction"]
