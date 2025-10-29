package com.skinmate.auth.exception;

import com.skinmate.auth.domain.ResponseCode;
import com.skinmate.auth.dto.ApiResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {
    
    // CustomException 처리
    @ExceptionHandler(CustomException.class)
    public ResponseEntity<ApiResponse<Void>> handleCustomException(CustomException e) {
        log.error("CustomException: {} - {}", e.getResponseCode(), e.getMessage());
        
        ApiResponse<Void> response = ApiResponse.error(
            e.getResponseCode().getCode(),
            e.getMessage()
        );
        
        return ResponseEntity
            .status(e.getResponseCode().getHttpStatus())
            .body(response);
    }
    
    // 기타 모든 예외 처리
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiResponse<Void>> handleException(Exception e) {
        log.error("Unexpected exception", e);
        
        ApiResponse<Void> response = ApiResponse.error(
            ResponseCode.INTERNAL_SERVER_ERROR.getCode(),
            ResponseCode.INTERNAL_SERVER_ERROR.getMessage()
        );
        
        return ResponseEntity
            .status(ResponseCode.INTERNAL_SERVER_ERROR.getHttpStatus())
            .body(response);
    }
}
