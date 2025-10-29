package com.skinmate.auth.exception;

import com.skinmate.auth.domain.ResponseCode;
import lombok.Getter;

@Getter
public class CustomException extends RuntimeException {
    private final ResponseCode responseCode;
    
    // 생성자 1: ResponseCode의 기본 메시지 사용
    public CustomException(ResponseCode responseCode) {
        super(responseCode.getMessage());
        this.responseCode = responseCode;
    }
    
    // 생성자 2: 동적으로 커스텀 메시지 사용
    public CustomException(ResponseCode responseCode, String customMessage) {
        super(customMessage);
        this.responseCode = responseCode;
    }
}
