package com.skinmate.auth.oauth.handler;

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
    
    @Override
    public void onAuthenticationFailure(HttpServletRequest request, HttpServletResponse response,
                                      AuthenticationException exception) throws IOException, ServletException {
        
        log.error("OAuth2 로그인 실패: {}", exception.getMessage());
        
        // 에러 응답 (JSON 형태로 반환)
        response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
        response.setContentType("application/json;charset=UTF-8");
        
        String errorResponse = String.format(
            "{\"error\":\"OAuth2_LOGIN_FAILED\",\"message\":\"%s\",\"timestamp\":\"%s\"}",
            exception.getMessage(),
            System.currentTimeMillis()
        );
        
        response.getWriter().write(errorResponse);
    }
}
