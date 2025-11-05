package com.skinmate.auth.repository;

import com.skinmate.auth.domain.RefreshToken;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.time.LocalDateTime;
import java.util.Optional;

public interface RefreshTokenRepository extends JpaRepository<RefreshToken, Integer> {
    
    // 토큰으로 조회
    Optional<RefreshToken> findByRefreshToken(String refreshToken);
    
    // 회원 ID로 조회
    Optional<RefreshToken> findByMemberId(Integer memberId);
    
    // 회원 ID로 삭제
    @Modifying
    @Query("DELETE FROM RefreshToken rt WHERE rt.memberId = :memberId")
    void deleteByMemberId(@Param("memberId") Integer memberId);
    
    // 만료된 토큰 삭제
    @Modifying
    @Query("DELETE FROM RefreshToken rt WHERE rt.expiresAt < :now")
    void deleteByExpiresAtBefore(@Param("now") LocalDateTime now);
}
