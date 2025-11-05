"""
LLM 관련 유틸리티 함수
"""
import json
from typing import Dict, Any


def parse_llm_json(text: str) -> Dict[str, Any]:
    """
    LLM 응답에서 JSON을 파싱하는 유틸리티 함수
    
    코드 블록(```json ... ``` 또는 ``` ... ```)을 자동으로 제거하고
    순수 JSON만 추출하여 파싱합니다.
    
    Args:
        text: LLM의 응답 텍스트
        
    Returns:
        Dict[str, Any]: 파싱된 JSON 객체
        
    Raises:
        ValueError: JSON 파싱에 실패한 경우
    """
    # 앞뒤 공백 제거
    stripped = text.strip()
    
    # 코드블록 제거 시도 (```json ... ``` 또는 ``` ... ```)
    if stripped.startswith("```"):
        try:
            # 백틱 제거
            stripped = stripped.strip('`')
            
            # 첫 줄에 'json' 태그가 있으면 제거
            lines = stripped.splitlines()
            if lines and lines[0].strip().lower() in ['json', 'JSON']:
                lines = lines[1:]
            stripped = "\n".join(lines)
        except Exception:
            pass
    
    # 순수 JSON 파싱 시도
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        # 실패 시 중괄호 구간만 추출 시도
        start = stripped.find('{')
        end = stripped.rfind('}')
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(stripped[start:end+1])
            except json.JSONDecodeError:
                pass
        
        # 모든 시도 실패
        raise ValueError(f"LLM 응답을 JSON으로 파싱할 수 없습니다: {text[:100]}...")

