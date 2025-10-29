package com.skinmate.auth.oauth.handler;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.skinmate.auth.domain.RefreshToken;
import com.skinmate.auth.dto.ApiResponse;
import com.skinmate.auth.dto.TokenResponse;
import com.skinmate.auth.exception.ResponseCode;
import com.skinmate.auth.jwt.JwtTokenProvider;
import com.skinmate.auth.repository.RefreshTokenRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.core.Authentication;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.security.web.authentication.AuthenticationSuccessHandler;
import org.springframework.stereotype.Component;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.time.LocalDateTime;

@Component
@RequiredArgsConstructor
@Slf4j
public class OAuth2AuthenticationSuccessHandler implements AuthenticationSuccessHandler {
    
    private final JwtTokenProvider jwtTokenProvider;
    private final RefreshTokenRepository refreshTokenRepository;
    private final ObjectMapper objectMapper;
    
    @Override
    public void onAuthenticationSuccess(HttpServletRequest request, HttpServletResponse response,
                                      Authentication authentication) throws IOException, ServletException {
        
        OAuth2User oAuth2User = (OAuth2User) authentication.getPrincipal();
        
        // OAuth2User에서 Member 정보 추출 (CustomOAuth2UserService에서 저장된 정보)
        Long memberId = oAuth2User.getAttribute("memberId");
        String role = oAuth2User.getAttribute("role");
        
        if (memberId == null || role == null) {
            ApiResponse<Void> errorResponse = ApiResponse.error(
                ResponseCode.OAUTH2_LOGIN_FAILED.getCode(),
                "Member 정보를 찾을 수 없습니다."
            );
            response.setStatus(ResponseCode.OAUTH2_LOGIN_FAILED.getHttpStatus().value());
            response.setContentType("application/json;charset=UTF-8");
            response.getWriter().write(objectMapper.writeValueAsString(errorResponse));
            return;
        }
        
        // log.info("OAuth2 로그인 성공 - Member ID: {}, Role: {}", memberId, role);
        
        // JWT 토큰 생성
        String accessToken = jwtTokenProvider.generateAccessToken(memberId, role);
        String refreshToken = jwtTokenProvider.generateRefreshToken(memberId);
        
        // Refresh Token을 DB에 저장
        RefreshToken refreshTokenEntity = RefreshToken.builder()
                .memberId(memberId)
                .refreshToken(refreshToken)
                .expiresAt(LocalDateTime.now().plusDays(7)) // 7일 후 만료
                .createdAt(LocalDateTime.now())
                .build();
        
        refreshTokenRepository.save(refreshTokenEntity);
        
        // log.info("JWT 토큰 발급 완료 - Access Token: {}, Refresh Token 저장됨", accessToken.substring(0, 20) + "...");
        
        // Bearer Token 방식: Response Body로 토큰 반환
        TokenResponse tokenResponse = new TokenResponse(accessToken, refreshToken);
        ApiResponse<TokenResponse> apiResponse = ApiResponse.success(
            ResponseCode.SUCCESS.getCode(),
            "로그인 성공",
            tokenResponse
        );
        
        response.setStatus(ResponseCode.SUCCESS.getHttpStatus().value());
        response.setContentType("application/json;charset=UTF-8");
        response.getWriter().write(objectMapper.writeValueAsString(apiResponse));
    }
}
