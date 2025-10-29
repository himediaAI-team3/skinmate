package com.skinmate.auth.service;

import com.skinmate.auth.domain.Member;
import com.skinmate.auth.domain.RefreshToken;
import com.skinmate.auth.domain.ResponseCode;
import com.skinmate.auth.exception.CustomException;
import com.skinmate.auth.jwt.JwtTokenProvider;
import com.skinmate.auth.repository.MemberRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Slf4j
@Transactional
public class AuthService {
    
    private final JwtTokenProvider jwtTokenProvider;
    private final RefreshTokenService refreshTokenService;
    private final MemberRepository memberRepository;
    
    // 토큰 갱신
    public String refreshAccessToken(String refreshToken) {
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
        Member member = memberRepository.findById(tokenEntity.getMemberId())
                .orElseThrow(() -> new CustomException(ResponseCode.MEMBER_NOT_FOUND));
        
        // 5. 새로운 Access Token 발급
        String newAccessToken = jwtTokenProvider.generateAccessToken(
                member.getMemberId(),
                member.getRole()
        );
        
        return newAccessToken;
    }
    
    // 로그아웃 (Refresh Token 삭제)
    public void logout(Long memberId) {
        refreshTokenService.deleteByMemberId(memberId);
    }
}
