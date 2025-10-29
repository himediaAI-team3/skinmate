package com.skinmate.auth.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class ApiResponse<T> {
    private boolean success;
    private int code;
    private String message;
    private T data;
    
    // 성공 응답 (data 없음)
    public static <T> ApiResponse<T> success(int code, String message) {
        return new ApiResponse<>(true, code, message, null);
    }
    
    // 성공 응답 (data 있음)
    public static <T> ApiResponse<T> success(int code, String message, T data) {
        return new ApiResponse<>(true, code, message, data);
    }
    
    // 에러 응답
    public static <T> ApiResponse<T> error(int code, String message) {
        return new ApiResponse<>(false, code, message, null);
    }
}
