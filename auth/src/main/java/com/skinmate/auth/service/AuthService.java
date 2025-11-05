package com.skinmate.auth.service;

import com.skinmate.auth.domain.Member;
import com.skinmate.auth.domain.RefreshToken;
import com.skinmate.auth.domain.ResponseCode;
import com.skinmate.auth.dto.TokenResponse;
import com.skinmate.auth.exception.CustomException;
import com.skinmate.auth.jwt.JwtTokenProvider;
import com.skinmate.auth.dto.KakaoUserDto;
import com.skinmate.auth.dto.KakaoSignupRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;

@Service
@RequiredArgsConstructor
@Slf4j
@Transactional
public class AuthService {
    
    private final JwtTokenProvider jwtTokenProvider;
    private final RefreshTokenService refreshTokenService;
    private final MemberService memberService;

    @Value("${spring.security.oauth2.client.registration.kakao.client-id}")
    private String kakaoClientId;

    @Value("${spring.security.oauth2.client.registration.kakao.client-secret:}")
    private String kakaoClientSecret;

    @Value("${spring.security.oauth2.client.registration.kakao.redirect-uri}")
    private String kakaoRedirectUri;

    @Value("${spring.security.oauth2.client.provider.kakao.token-uri}")
    private String kakaoTokenUri;

    @Value("${spring.security.oauth2.client.provider.kakao.user-info-uri}")
    private String kakaoUserInfoUri;

    // 카카오 인가코드로 로그인 처리: 토큰 교환 → 사용자 조회 → 우리 JWT 발급
    public TokenResponse loginWithKakaoCode(String code) {
        // 1) 클라이언트에서 받은 인가코드로 카카오에 토큰 교환
        String kakaoAccessToken = exchangeCodeForKakaoAccessToken(code);

        // 2) kakaoAccessToken을 통해 카카오 사용자 정보 조회
        KakaoUserDto kakaoUser = fetchKakaoUser(kakaoAccessToken);

        // 3) 우리 회원 매핑/생성
        Member member = memberService.getOrCreateKakaoMember(
                new KakaoSignupRequest(String.valueOf(kakaoUser.getId()), kakaoUser.getNickname())
        );

        // 4) 우리 JWT 발급 및 Refresh Token 저장
        String accessToken = jwtTokenProvider.generateAccessToken(member.getMemberId(), member.getRole());
        String refreshToken = jwtTokenProvider.generateRefreshToken(member.getMemberId());
        refreshTokenService.saveRefreshToken(
                member.getMemberId(),
                refreshToken,
                java.time.LocalDateTime.now().plusDays(7)
        );

        return new TokenResponse(accessToken, refreshToken);
    }
    
    // 토큰 갱신 (Refresh Token 회전 포함)
    public TokenResponse refreshAccessToken(String refreshToken) {
        // 1. Refresh Token 검증
        if (!jwtTokenProvider.validateToken(refreshToken)) {
            throw new CustomException(ResponseCode.INVALID_TOKEN);
        }
        
        // 2. Refresh Token 만료 확인
        if (jwtTokenProvider.isTokenExpired(refreshToken)) {
            throw new CustomException(ResponseCode.TOKEN_EXPIRED);
        }
        
        // 3. DB에서 Refresh Token 조회
        RefreshToken tokenEntity = refreshTokenService.findByRefreshToken(refreshToken)
                .orElseThrow(() -> new CustomException(ResponseCode.REFRESH_TOKEN_NOT_FOUND));
        
        // 4. Member 조회
        Member member = memberService.getById(tokenEntity.getMemberId());
        
        // 5. 기존 Refresh Token 삭제 (회전)
        refreshTokenService.deleteByMemberId(member.getMemberId());
        
        // 6. 새로운 Access Token 발급
        String newAccessToken = jwtTokenProvider.generateAccessToken(
                member.getMemberId(),
                member.getRole()
        );
        
        // 7. 새로운 Refresh Token 발급 및 저장
        String newRefreshToken = jwtTokenProvider.generateRefreshToken(member.getMemberId());
        refreshTokenService.saveRefreshToken(
                member.getMemberId(),
                newRefreshToken,
                java.time.LocalDateTime.now().plusDays(7) // 7일 후 만료
        );
        
        // 8. 두 토큰 모두 반환
        return new TokenResponse(newAccessToken, newRefreshToken);
    }
    
    // 로그아웃 (Refresh Token 삭제)
    public void logout(Integer memberId) {
        refreshTokenService.deleteByMemberId(memberId);
    }

    private String exchangeCodeForKakaoAccessToken(String code) {
        String url = kakaoTokenUri;

        MultiValueMap<String, String> params = new LinkedMultiValueMap<>();
        params.add("grant_type", "authorization_code");
        params.add("client_id", kakaoClientId);
        params.add("redirect_uri", kakaoRedirectUri);
        params.add("code", code);
        if (kakaoClientSecret != null && !kakaoClientSecret.isBlank()) {
            params.add("client_secret", kakaoClientSecret);
        }

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_FORM_URLENCODED);

        RestTemplate restTemplate = new RestTemplate();
        ResponseEntity<java.util.Map> response = restTemplate.postForEntity(
                url,
                new HttpEntity<>(params, headers),
                java.util.Map.class
        );

        if (!response.getStatusCode().is2xxSuccessful() || response.getBody() == null) {
            throw new CustomException(ResponseCode.OAUTH2_LOGIN_FAILED, "카카오 토큰 교환 실패");
        }
        Object token = response.getBody().get("access_token");
        if (token == null) {
            throw new CustomException(ResponseCode.OAUTH2_LOGIN_FAILED, "카카오 access_token 누락");
        }
        return token.toString();
    }

    private KakaoUserDto fetchKakaoUser(String kakaoAccessToken) {
        String url = kakaoUserInfoUri;

        HttpHeaders headers = new HttpHeaders();
        headers.setBearerAuth(kakaoAccessToken);

        RestTemplate restTemplate = new RestTemplate();
        ResponseEntity<java.util.Map> response = restTemplate.exchange(
                url,
                HttpMethod.GET,
                new HttpEntity<>(headers),
                java.util.Map.class
        );

        if (!response.getStatusCode().is2xxSuccessful() || response.getBody() == null) {
            throw new CustomException(ResponseCode.OAUTH2_LOGIN_FAILED, "카카오 사용자 정보 조회 실패");
        }

        java.util.Map body = response.getBody();
        Object id = body.get("id");
        if (id == null) {
            throw new CustomException(ResponseCode.OAUTH2_LOGIN_FAILED, "카카오 사용자 id 누락");
        }

        // kakao_account.profile.nickname 등 추출 (nickname -> member.name으로 매핑됨)
        String nickname = null;
        Object accountObj = body.get("kakao_account");
        if (accountObj instanceof java.util.Map) {
            java.util.Map account = (java.util.Map) accountObj;
            Object profileObj = account.get("profile");

            if (profileObj instanceof java.util.Map) {
                Object nickObj = ((java.util.Map) profileObj).get("nickname");

                if (nickObj != null) {
                    nickname = String.valueOf(nickObj);
                }
            }
        }

        return new KakaoUserDto(Long.parseLong(String.valueOf(id)), nickname);
    }
}
