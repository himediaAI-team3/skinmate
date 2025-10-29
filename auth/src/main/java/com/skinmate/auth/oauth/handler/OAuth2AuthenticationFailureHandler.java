package com.skinmate.auth.oauth.handler;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.skinmate.auth.dto.ApiResponse;
import com.skinmate.auth.exception.ResponseCode;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.web.authentication.AuthenticationFailureHandler;
import org.springframework.stereotype.Component;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

@Component
@Slf4j
public class OAuth2AuthenticationFailureHandler implements AuthenticationFailureHandler {
    
    private final ObjectMapper objectMapper = new ObjectMapper();
    
    @Override
    public void onAuthenticationFailure(HttpServletRequest request, HttpServletResponse response,
                                      AuthenticationException exception) throws IOException, ServletException {
        
        log.error("OAuth2 로그인 실패: {}", exception.getMessage());
        
        // ApiResponse로 에러 응답 생성
        ApiResponse<Void> errorResponse = ApiResponse.error(
            ResponseCode.OAUTH2_LOGIN_FAILED.getCode(),
            ResponseCode.OAUTH2_LOGIN_FAILED.getMessage() + ": " + exception.getMessage()
        );
        
        // JSON 응답 설정
        response.setStatus(ResponseCode.OAUTH2_LOGIN_FAILED.getHttpStatus().value());
        response.setContentType("application/json;charset=UTF-8");
        
        // ApiResponse를 JSON으로 변환하여 응답
        String jsonResponse = objectMapper.writeValueAsString(errorResponse);
        response.getWriter().write(jsonResponse);
    }
}
