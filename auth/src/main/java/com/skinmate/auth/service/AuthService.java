package com.skinmate.auth.service;

import com.skinmate.auth.domain.Member;
import com.skinmate.auth.domain.RefreshToken;
import com.skinmate.auth.domain.ResponseCode;
import com.skinmate.auth.dto.TokenResponse;
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
        Member member = memberRepository.findById(tokenEntity.getMemberId())
                .orElseThrow(() -> new CustomException(ResponseCode.MEMBER_NOT_FOUND));
        
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
    public void logout(Long memberId) {
        refreshTokenService.deleteByMemberId(memberId);
    }
}
