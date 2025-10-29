package com.skinmate.auth.exception;

import com.skinmate.auth.domain.ResponseCode;
import com.skinmate.auth.dto.ApiResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {
    
    // @Valid 필드에 발생한 예외 처리
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ApiResponse<Void>> handleValidationException(MethodArgumentNotValidException ex) {
        String errorMessage = ex.getBindingResult().getAllErrors().get(0).getDefaultMessage();
        log.error("handleValidationException : {}", errorMessage);
        
        return ResponseEntity
                .status(ResponseCode.INVALID_REQUEST.getHttpStatus())
                .body(ApiResponse.error(ResponseCode.INVALID_REQUEST.getCode(), errorMessage));
    }
    
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
