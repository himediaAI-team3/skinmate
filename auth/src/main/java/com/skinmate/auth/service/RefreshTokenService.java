package com.skinmate.auth.service;

import com.skinmate.auth.domain.RefreshToken;
import com.skinmate.auth.repository.RefreshTokenRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.Optional;

@Service
@RequiredArgsConstructor
@Slf4j
@Transactional
public class RefreshTokenService {
    
    private final RefreshTokenRepository refreshTokenRepository;
    
    // Refresh Token 저장
    public RefreshToken saveRefreshToken(Integer memberId, String refreshToken, LocalDateTime expiresAt) {
        // 기존 토큰이 있으면 삭제
        refreshTokenRepository.findByMemberId(memberId)
                .ifPresent(refreshTokenRepository::delete);
        
        RefreshToken tokenEntity = RefreshToken.builder()
                .memberId(memberId)
                .refreshToken(refreshToken)
                .expiresAt(expiresAt)
                .createdAt(LocalDateTime.now())
                .createdId(memberId)
                .build();
        
        return refreshTokenRepository.save(tokenEntity);
    }
    
    // Refresh Token으로 조회
    @Transactional(readOnly = true)
    public Optional<RefreshToken> findByRefreshToken(String refreshToken) {
        return refreshTokenRepository.findByRefreshToken(refreshToken);
    }
    
    // Member ID로 조회
    @Transactional(readOnly = true)
    public Optional<RefreshToken> findByMemberId(Integer memberId) {
        return refreshTokenRepository.findByMemberId(memberId);
    }
    
    // Member ID로 삭제 (로그아웃 시)
    public void deleteByMemberId(Integer memberId) {
        refreshTokenRepository.deleteByMemberId(memberId);
    }
    
}
