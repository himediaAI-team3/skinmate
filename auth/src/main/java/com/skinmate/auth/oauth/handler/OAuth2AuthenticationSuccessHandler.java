package com.skinmate.auth.oauth.handler;

import com.skinmate.auth.domain.Member;
import com.skinmate.auth.domain.RefreshToken;
import com.skinmate.auth.jwt.JwtTokenProvider;
import com.skinmate.auth.repository.RefreshTokenRepository;
import com.skinmate.auth.util.CookieUtils;
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
    private final CookieUtils cookieUtils;
    private final RefreshTokenRepository refreshTokenRepository;
    
    @Override
    public void onAuthenticationSuccess(HttpServletRequest request, HttpServletResponse response,
                                      Authentication authentication) throws IOException, ServletException {
        
        OAuth2User oAuth2User = (OAuth2User) authentication.getPrincipal();
        
        // OAuth2User에서 Member 정보 추출 (CustomOAuth2UserService에서 저장된 정보)
        Long memberId = oAuth2User.getAttribute("memberId");
        String role = oAuth2User.getAttribute("role");
        
        if (memberId == null || role == null) {
            log.error("OAuth2User에서 Member 정보를 찾을 수 없습니다.");
            response.sendRedirect("/error");
            return;
        }
        
        log.info("OAuth2 로그인 성공 - Member ID: {}, Role: {}", memberId, role);
        
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
        
        // HttpOnly 쿠키로 토큰 전달
        cookieUtils.setAccessTokenCookie(response, accessToken);
        cookieUtils.setRefreshTokenCookie(response, refreshToken);
        
        log.info("JWT 토큰 발급 완료 - Access Token: {}, Refresh Token 저장됨", accessToken.substring(0, 20) + "...");
        
        // 프론트엔드로 리다이렉트 (실제 프론트엔드 URL로 변경 필요)
        response.sendRedirect("https://naver.com");
    }
}
